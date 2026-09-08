#!/usr/bin/env python3
"""Point-and-click GUI for the Innohealth ThermalMesh Pipeline.

No command line needed: browse for your input files, click Run, watch the
log, then open the output folder. Launched via the RunThermalMesh
double-click scripts in the repository root (Mac: .command, Windows: .bat,
Linux: .sh), or directly with ``python3 scripts/gui.py``.
"""

from __future__ import annotations

import logging
import queue
import subprocess
import sys
import threading
import traceback
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, StringVar, Tk, X, filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))


class ThermalMeshApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        root.title("Innohealth ThermalMesh Pipeline")
        root.geometry("760x600")
        root.minsize(640, 480)

        self.mesh_var = StringVar()
        self.initial_mesh_var = StringVar()
        self.thermal_var = StringVar()
        self.cameras_var = StringVar()
        self.output_var = StringVar(value=str(ROOT_DIR / "output"))
        self.config_var = StringVar()

        self.log_queue: queue.Queue[str] = queue.Queue()
        self.run_button: ttk.Button
        self.progress: ttk.Progressbar
        self.log_text: ScrolledText

        self._build_layout()
        self.root.after(100, self._drain_log_queue)

    # ---------------------------------------------------------------- UI

    def _build_layout(self) -> None:
        intro = ttk.Label(
            self.root,
            text="Fill in the fields below (or click \"Generate Demo Dataset\" to try it "
            "with no real data yet), then click Run Pipeline.",
            wraplength=720, justify=LEFT,
        )
        intro.pack(fill=X, padx=10, pady=(10, 0))

        self._file_row("Final mesh (.ply) *", self.mesh_var, self._browse_file([("PLY mesh", "*.ply")]))
        self._file_row("Initial mesh (.ply) - optional", self.initial_mesh_var, self._browse_file([("PLY mesh", "*.ply")]))
        self._file_row("Thermal data folder *", self.thermal_var, self._browse_dir())
        self._file_row("Cameras file (.json) *", self.cameras_var, self._browse_file([("JSON", "*.json")]))
        self._file_row("Output folder", self.output_var, self._browse_dir())
        self._file_row("Config file (.yaml) - optional", self.config_var, self._browse_file([("YAML", "*.yaml *.yml")]))

        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=X, padx=10, pady=8)
        ttk.Button(button_frame, text="Generate Demo Dataset", command=self._generate_demo).pack(side=LEFT, padx=4)
        self.run_button = ttk.Button(button_frame, text="Run Pipeline", command=self._run_pipeline)
        self.run_button.pack(side=LEFT, padx=4)
        ttk.Button(button_frame, text="Open Output Folder", command=self._open_output).pack(side=LEFT, padx=4)

        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill=X, padx=10, pady=(0, 8))

        self.log_text = ScrolledText(self.root, height=20, state="disabled", bg="black", fg="#00ff66", font=("Courier", 10))
        self.log_text.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

    def _file_row(self, label: str, var: StringVar, browse) -> None:
        frame = ttk.Frame(self.root)
        frame.pack(fill=X, padx=10, pady=4)
        ttk.Label(frame, text=label, width=28).pack(side=LEFT)
        ttk.Entry(frame, textvariable=var).pack(side=LEFT, fill=X, expand=True, padx=6)
        ttk.Button(frame, text="Browse...", command=lambda: browse(var)).pack(side=RIGHT)

    def _browse_file(self, filetypes):
        def handler(var: StringVar) -> None:
            path = filedialog.askopenfilename(filetypes=filetypes)
            if path:
                var.set(path)

        return handler

    def _browse_dir(self):
        def handler(var: StringVar) -> None:
            path = filedialog.askdirectory()
            if path:
                var.set(path)

        return handler

    # ------------------------------------------------------------ logging

    def _log(self, message: str) -> None:
        self.log_queue.put(message)

    def _drain_log_queue(self) -> None:
        while not self.log_queue.empty():
            message = self.log_queue.get_nowait()
            self.log_text.configure(state="normal")
            self.log_text.insert(END, message + "\n")
            self.log_text.see(END)
            self.log_text.configure(state="disabled")
        self.root.after(100, self._drain_log_queue)

    def _clear_log(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", END)
        self.log_text.configure(state="disabled")

    def _set_running(self, running: bool) -> None:
        self.run_button.configure(state="disabled" if running else "normal")
        if running:
            self.progress.start(10)
        else:
            self.progress.stop()

    # ------------------------------------------------------------- actions

    def _generate_demo(self) -> None:
        self._set_running(True)
        self._clear_log()

        def worker() -> None:
            # Tkinter widgets/variables are not thread-safe: this background thread only
            # does file I/O and computation, then hands results back via root.after() so
            # every actual UI mutation happens on the main thread.
            try:
                from thermalmesh.synthetic import generate_synthetic_dataset

                demo_dir = ROOT_DIR / "examples" / "synthetic_dataset"
                self._log(f"Generating a demo 3D object + synthetic thermal views in {demo_dir} ...")
                generate_synthetic_dataset(demo_dir, num_views=12)

                def apply_success() -> None:
                    self.mesh_var.set(str(demo_dir / "final_mesh.ply"))
                    self.initial_mesh_var.set(str(demo_dir / "initial_mesh.ply"))
                    self.thermal_var.set(str(demo_dir / "thermal"))
                    self.cameras_var.set(str(demo_dir / "cameras.json"))
                    self.config_var.set(str(ROOT_DIR / "config" / "synthetic.yaml"))

                self.root.after(0, apply_success)
                self._log("Demo dataset ready -- fields filled in automatically.")
                self._log("Click \"Run Pipeline\" to process it.")
            except Exception as exc:  # noqa: BLE001
                self._log(f"ERROR generating demo dataset: {exc}")
                self._log(traceback.format_exc())
            finally:
                self.root.after(0, lambda: self._set_running(False))

        threading.Thread(target=worker, daemon=True).start()

    def _run_pipeline(self) -> None:
        mesh = self.mesh_var.get().strip()
        thermal = self.thermal_var.get().strip()
        cameras = self.cameras_var.get().strip()
        output = self.output_var.get().strip()

        if not mesh or not thermal or not cameras or not output:
            messagebox.showerror(
                "Missing input",
                "Final mesh, thermal data folder, cameras file, and output folder are all required.",
            )
            return

        self._set_running(True)
        self._clear_log()

        def worker() -> None:
            handler = _QueueLogHandler(self._log)
            handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
            root_logger = logging.getLogger("thermalmesh")
            root_logger.setLevel(logging.INFO)
            root_logger.addHandler(handler)
            try:
                from thermalmesh.pipeline.runner import run_pipeline

                initial_mesh = self.initial_mesh_var.get().strip() or None
                config_path = self.config_var.get().strip() or None

                run_pipeline(
                    mesh_path=mesh, thermal_dir=thermal, cameras_path=cameras,
                    output_dir=output, initial_mesh_path=initial_mesh, config_path=config_path,
                )
                self._log("")
                self._log("DONE. Pipeline completed successfully.")
                self._log(f"Outputs written to: {output}")
                self.root.after(0, lambda: messagebox.showinfo("Done", f"Pipeline completed.\n\nOutputs written to:\n{output}"))
            except Exception as exc:  # noqa: BLE001
                self._log(f"ERROR: {exc}")
                self._log(traceback.format_exc())
                self.root.after(0, lambda: messagebox.showerror("Pipeline failed", str(exc)))
            finally:
                root_logger.removeHandler(handler)
                self.root.after(0, lambda: self._set_running(False))

        threading.Thread(target=worker, daemon=True).start()

    def _open_output(self) -> None:
        output = Path(self.output_var.get().strip() or "output")
        if not output.exists():
            messagebox.showwarning("Not found", f"Output folder does not exist yet:\n{output}")
            return
        if sys.platform == "darwin":
            subprocess.run(["open", str(output)])
        elif sys.platform.startswith("win"):
            subprocess.run(["explorer", str(output)])
        else:
            subprocess.run(["xdg-open", str(output)])


class _QueueLogHandler(logging.Handler):
    def __init__(self, sink) -> None:
        super().__init__()
        self._sink = sink

    def emit(self, record: logging.LogRecord) -> None:
        self._sink(self.format(record))


def main() -> None:
    root = Tk()
    ThermalMeshApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
