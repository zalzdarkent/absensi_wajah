import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/status-badge";
import { Plus, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import pool from "@/lib/db";
import { RowDataPacket } from "mysql2";

interface Employee {
  employee_id: number;
  employee_code: string;
  full_name: string;
  email: string;
  phone: string;
  department: string;
  position: string;
  status: string;
  photo_count: number;
  created_at: string;
}

async function getEmployees(): Promise<Employee[]> {
  try {
    const [rows] = await pool.query<RowDataPacket[]>(
      `SELECT 
        e.employee_id,
        e.employee_code,
        e.full_name,
        e.email,
        e.phone,
        e.department,
        e.position,
        e.status,
        e.created_at,
        COUNT(fe.encoding_id) as photo_count
      FROM employees e
      LEFT JOIN face_encodings fe ON e.employee_id = fe.employee_id
      GROUP BY e.employee_id
      ORDER BY e.created_at DESC`
    );
    
    return rows as Employee[];
  } catch (error) {
    console.error('Error fetching employees:', error);
    return [];
  }
}

export default async function EmployeesPage() {
  const employees = await getEmployees();

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Daftar Karyawan</h1>
          <p className="text-muted-foreground">
            Kelola karyawan dan data wajah mereka
          </p>
        </div>
        <Link href="/employees/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Tambah Karyawan
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Semua Karyawan ({employees.length})</CardTitle>
            <div className="relative w-64">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Cari karyawan..." className="pl-8" />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {employees.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-4">Belum ada karyawan terdaftar</p>
              <Link href="/employees/new">
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Tambah Karyawan Pertama
                </Button>
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3 font-medium">Kode</th>
                    <th className="text-left p-3 font-medium">Nama</th>
                    <th className="text-left p-3 font-medium">Email</th>
                    <th className="text-left p-3 font-medium">Department</th>
                    <th className="text-left p-3 font-medium">Posisi</th>
                    <th className="text-left p-3 font-medium">Foto</th>
                    <th className="text-left p-3 font-medium">Status</th>
                    <th className="text-left p-3 font-medium">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {employees.map((employee) => (
                    <tr key={employee.employee_id} className="border-b hover:bg-muted/50">
                      <td className="p-3 font-mono text-sm">{employee.employee_code}</td>
                      <td className="p-3 font-medium">{employee.full_name}</td>
                      <td className="p-3 text-sm text-muted-foreground">
                        {employee.email || '-'}
                      </td>
                      <td className="p-3 text-sm">{employee.department || '-'}</td>
                      <td className="p-3 text-sm">{employee.position || '-'}</td>
                      <td className="p-3">
                        <span className="text-sm bg-primary/10 text-primary px-2 py-1 rounded">
                          {employee.photo_count} foto
                        </span>
                      </td>
                      <td className="p-3">
                        <StatusBadge status={employee.status} />
                      </td>
                      <td className="p-3">
                        <Link href={`/employees/${employee.employee_id}`}>
                          <Button variant="ghost" size="sm">
                            Detail
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
