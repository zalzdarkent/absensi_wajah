import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/status-badge";
import { ArrowLeft, Mail, Phone, Briefcase, Building } from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";
import { id as localeId } from "date-fns/locale";
import pool from "@/lib/db";
import { RowDataPacket } from "mysql2";

interface EmployeeDetails {
  employee: {
    employee_id: number;
    employee_code: string;
    full_name: string;
    email: string;
    phone: string;
    department: string;
    position: string;
    status: string;
    created_at: string;
  };
  photos: Array<{
    encoding_id: number;
    image_path: string;
    quality_score: number;
    is_primary: boolean;
    created_at: string;
  }>;
  attendance: Array<{
    attendance_id: number;
    attendance_date: string;
    check_in_time: string;
    check_out_time: string;
    status: string;
    check_in_confidence: number;
    check_out_confidence: number;
  }>;
}

async function getEmployeeDetails(id: string): Promise<EmployeeDetails | null> {
  try {
    // Get employee details
    const [employees] = await pool.query<RowDataPacket[]>(
      `SELECT * FROM employees WHERE employee_id = ?`,
      [id]
    );
    
    if (employees.length === 0) {
      return null;
    }
    
    // Get face encodings/photos
    const [photos] = await pool.query<RowDataPacket[]>(
      `SELECT 
        encoding_id,
        image_path,
        quality_score,
        is_primary,
        created_at
      FROM face_encodings
      WHERE employee_id = ?
      ORDER BY is_primary DESC, created_at ASC`,
      [id]
    );
    
    // Get attendance history
    const [attendance] = await pool.query<RowDataPacket[]>(
      `SELECT 
        attendance_id,
        attendance_date,
        check_in_time,
        check_out_time,
        status,
        check_in_confidence,
        check_out_confidence
      FROM attendance_records
      WHERE employee_id = ?
      ORDER BY attendance_date DESC
      LIMIT 30`,
      [id]
    );
    
    return {
      employee: employees[0] as any,
      photos: photos as any[],
      attendance: attendance as any[]
    };
  } catch (error) {
    console.error('Error fetching employee details:', error);
    return null;
  }
}

export default async function EmployeeDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const data = await getEmployeeDetails(id);
  
  if (!data) {
    return (
      <div className="flex flex-col gap-6 p-6">
        <div className="flex items-center gap-4">
          <Link href="/employees">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Kembali
            </Button>
          </Link>
        </div>
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-muted-foreground">Employee not found or database connection error</p>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  const { employee, photos, attendance } = data;

  const attendanceRate = attendance.length > 0
    ? Math.round((attendance.filter(a => a.status === 'present').length / attendance.length) * 100)
    : 0;

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center gap-4">
        <Link href="/employees">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Kembali
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">{employee.full_name}</h1>
          <p className="text-muted-foreground">{employee.employee_code}</p>
        </div>
        <StatusBadge status={employee.status} />
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Employee Info */}
        <Card>
          <CardHeader>
            <CardTitle>Informasi Karyawan</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {employee.email && (
              <div className="flex items-start gap-3">
                <Mail className="h-4 w-4 mt-0.5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p className="text-sm font-medium">{employee.email}</p>
                </div>
              </div>
            )}
            {employee.phone && (
              <div className="flex items-start gap-3">
                <Phone className="h-4 w-4 mt-0.5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Telepon</p>
                  <p className="text-sm font-medium">{employee.phone}</p>
                </div>
              </div>
            )}
            {employee.department && (
              <div className="flex items-start gap-3">
                <Building className="h-4 w-4 mt-0.5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Department</p>
                  <p className="text-sm font-medium">{employee.department}</p>
                </div>
              </div>
            )}
            {employee.position && (
              <div className="flex items-start gap-3">
                <Briefcase className="h-4 w-4 mt-0.5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Posisi</p>
                  <p className="text-sm font-medium">{employee.position}</p>
                </div>
              </div>
            )}
            <div className="pt-4 border-t">
              <p className="text-sm text-muted-foreground">Terdaftar sejak</p>
              <p className="text-sm font-medium">
                {format(new Date(employee.created_at), "d MMMM yyyy", { locale: localeId })}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Face Photos */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Foto Wajah ({photos.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {photos.map((photo) => (
                <div key={photo.encoding_id} className="relative group">
                  <div className="aspect-square bg-muted rounded-lg overflow-hidden border-2 border-muted">
                    <img
                      src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/images/${photo.image_path}`}
                      alt="Employee face"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="absolute top-2 right-2">
                    {photo.is_primary && (
                      <span className="bg-primary text-primary-foreground text-xs px-2 py-1 rounded">
                        Primary
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1 text-center">
                    Quality: {(photo.quality_score * 100).toFixed(0)}%
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Attendance History */}
      <Card>
        <CardHeader>
          <CardTitle>Riwayat Kehadiran (30 hari terakhir)</CardTitle>
          <p className="text-sm text-muted-foreground">
            Tingkat kehadiran: <span className="font-bold text-primary">{attendanceRate}%</span>
          </p>
        </CardHeader>
        <CardContent>
          {attendance.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              Belum ada riwayat kehadiran
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3 font-medium">Tanggal</th>
                    <th className="text-left p-3 font-medium">Check-in</th>
                    <th className="text-left p-3 font-medium">Check-out</th>
                    <th className="text-left p-3 font-medium">Status</th>
                    <th className="text-left p-3 font-medium">Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {attendance.map((record) => (
                    <tr key={record.attendance_id} className="border-b hover:bg-muted/50">
                      <td className="p-3">
                        {format(new Date(record.attendance_date), "d MMM yyyy", { locale: localeId })}
                      </td>
                      <td className="p-3 text-sm">
                        {record.check_in_time
                          ? format(new Date(record.check_in_time), "HH:mm")
                          : '-'}
                      </td>
                      <td className="p-3 text-sm">
                        {record.check_out_time
                          ? format(new Date(record.check_out_time), "HH:mm")
                          : '-'}
                      </td>
                      <td className="p-3">
                        <StatusBadge status={record.status} />
                      </td>
                      <td className="p-3 text-sm">
                        {record.check_in_confidence
                          ? `${(record.check_in_confidence * 100).toFixed(0)}%`
                          : '-'}
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
