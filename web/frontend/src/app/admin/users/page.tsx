"use client";

import { useState } from "react";
import { Plus } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LoadingState } from "@/components/ui/states";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { toast } from "@/components/ui/toast";
import { useAdminUsers, useCreateAdminUser, useUpdateAdminUser } from "@/hooks/use-admin";
import { ApiError } from "@/lib/api/client";
import { formatDate } from "@/lib/utils";
import type { UserRole } from "@/types";

export default function AdminUsersPage() {
  const [search, setSearch] = useState("");
  const { data: users = [], isLoading } = useAdminUsers(search || undefined);
  const updateUser = useUpdateAdminUser();
  const createUser = useCreateAdminUser();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState({ email: "", full_name: "", password: "", role: "USER" as UserRole });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createUser.mutateAsync(form);
      setDialogOpen(false);
      setForm({ email: "", full_name: "", password: "", role: "USER" });
      toast({ title: "User created", tone: "success" });
    } catch (err) {
      toast({ title: "Could not create user", description: err instanceof ApiError ? err.message : undefined, tone: "danger" });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Users</h1>
          <p className="mt-1 text-muted">Manage platform access and roles.</p>
        </div>
        <Button onClick={() => setDialogOpen(true)}>
          <Plus className="h-4 w-4" /> Create User
        </Button>
      </div>

      <Input placeholder="Search by name or email..." value={search} onChange={(e) => setSearch(e.target.value)} className="max-w-sm" />

      {isLoading ? (
        <LoadingState label="Loading users..." />
      ) : (
        <div className="overflow-hidden rounded-2xl border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Projects</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Joined</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((u) => (
                <TableRow key={u.id}>
                  <TableCell>{u.full_name}</TableCell>
                  <TableCell className="text-muted">{u.email}</TableCell>
                  <TableCell>
                    <Badge tone={u.role === "ADMIN" ? "info" : "neutral"}>{u.role}</Badge>
                  </TableCell>
                  <TableCell className="font-mono">{u.project_count}</TableCell>
                  <TableCell>
                    <Badge tone={u.is_active ? "success" : "danger"}>{u.is_active ? "Active" : "Disabled"}</Badge>
                  </TableCell>
                  <TableCell className="text-muted">{formatDate(u.created_at)}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => updateUser.mutate({ id: u.id, payload: { role: u.role === "ADMIN" ? "USER" : "ADMIN" } })}
                      >
                        Make {u.role === "ADMIN" ? "User" : "Admin"}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => updateUser.mutate({ id: u.id, payload: { is_active: !u.is_active } })}
                      >
                        {u.is_active ? "Disable" : "Enable"}
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create user</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="space-y-1.5">
              <Label>Full name</Label>
              <Input required value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
            </div>
            <div className="space-y-1.5">
              <Label>Email</Label>
              <Input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            </div>
            <div className="space-y-1.5">
              <Label>Password</Label>
              <Input type="password" required minLength={8} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            </div>
            <div className="space-y-1.5">
              <Label>Role</Label>
              <Select value={form.role} onValueChange={(v) => setForm({ ...form, role: v as UserRole })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="USER">User</SelectItem>
                  <SelectItem value="ADMIN">Admin</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button type="submit" className="w-full" disabled={createUser.isPending}>
              {createUser.isPending ? "Creating..." : "Create user"}
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
