import { StatsCard } from "@/components/stats-card";
import { StatusBadge } from "@/components/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Users, UserCheck, Clock, UserX, Plus, LogIn, LogOut } from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";
import { id as localeId } from "date-fns/locale";
import pool from "@/lib/db";
import { RowDataPacket } from "mysql2";

interface StatsData {
  totalEmployees: number;
  today: {
    total: number;
    present: number;
    late: number;
    absent: number;
  };
  recentCheckIns: Array<{
    employee_code: string;
    full_name: string;
    department: string;
    check_in_time: string;
    status: string;
    check_in_confidence: number;
  }>;
}

async function getStats(): Promise<StatsData> {
  try {
    const today = new Date().toISOString().split('T')[0];
    
    // Total employees
    const [employeesCount] = await pool.query<RowDataPacket[]>(
      `SELECT COUNT(*) as total FROM employees WHERE status = 'active'`
    );
    
    // Today's attendance stats
    const [todayStats] = await pool.query<RowDataPacket[]>(
      `SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present,
        SUM(CASE WHEN status = 'late' THEN 1 ELSE 0 END) as late,
        SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END) as absent
      FROM attendance_records
      WHERE attendance_date = ?`,
      [today]
    );
    
    // Recent check-ins (last 10)
    const [recentCheckIns] = await pool.query<RowDataPacket[]>(
      `SELECT 
        a.check_in_time,
        a.status,
        a.check_in_confidence,
        e.employee_code,
        e.full_name,
        e.department
      FROM attendance_records a
      JOIN employees e ON a.employee_id = e.employee_id
      WHERE a.attendance_date = ? AND a.check_in_time IS NOT NULL
      ORDER BY a.check_in_time DESC
      LIMIT 10`,
      [today]
    );
    
    return {
      totalEmployees: employeesCount[0].total,
      today: {
        total: todayStats[0]?.total || 0,
        present: todayStats[0]?.present || 0,
        late: todayStats[0]?.late || 0,
        absent: employeesCount[0].total - (todayStats[0]?.total || 0)
      },
      recentCheckIns: recentCheckIns as any[]
    };
  } catch (error) {
    console.error('Error fetching stats:', error);
    return getEmptyStats();
  }
}

function getEmptyStats(): StatsData {
  return {
    totalEmployees: 0,
    today: {
      total: 0,
      present: 0,
      late: 0,
      absent: 0
    },
    recentCheckIns: []
  };
}

export default async function DashboardPage() {
  const stats = await getStats();
  
  const attendanceRate = stats.totalEmployees > 0
    ? Math.round((stats.today.total / stats.totalEmployees) * 100)
    : 0;

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            {format(new Date(), "EEEE, d MMMM yyyy", { locale: localeId })}
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/attendance?action=checkin">
            <Button>
              <LogIn className="mr-2 h-4 w-4" />
              Check In
            </Button>
          </Link>
          <Link href="/attendance?action=checkout">
            <Button variant="outline">
              <LogOut className="mr-2 h-4 w-4" />
              Check Out
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Karyawan"
          value={stats.totalEmployees}
          icon={Users}
          description="Karyawan terdaftar"
        />
        <StatsCard
          title="Hadir Hari Ini"
          value={stats.today.present}
          icon={UserCheck}
          description={`${attendanceRate}% tingkat kehadiran`}
        />
        <StatsCard
          title="Terlambat"
          value={stats.today.late}
          icon={Clock}
          description="Karyawan terlambat"
        />
        <StatsCard
          title="Tidak Hadir"
          value={stats.today.absent}
          icon={UserX}
          description="Belum absen"
        />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Recent Check-ins */}
        <Card>
          <CardHeader>
            <CardTitle>Check-in Terbaru</CardTitle>
          </CardHeader>
          <CardContent>
            {stats.recentCheckIns.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                Belum ada check-in hari ini
              </p>
            ) : (
              <div className="space-y-4">
                {stats.recentCheckIns.map((record, idx) => (
                  <div key={idx} className="flex items-center justify-between border-b pb-3 last:border-0">
                    <div>
                      <p className="font-medium">{record.full_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {record.employee_code} • {record.department || 'N/A'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">
                        {format(new Date(record.check_in_time), "HH:mm")}
                      </p>
                      <StatusBadge status={record.status} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link href="/employees/new" className="block">
              <Button variant="outline" className="w-full justify-start">
                <Plus className="mr-2 h-4 w-4" />
                Daftarkan Karyawan Baru
              </Button>
            </Link>
            <Link href="/attendance" className="block">
              <Button variant="outline" className="w-full justify-start">
                <Clock className="mr-2 h-4 w-4" />
                Lihat Semua Kehadiran
              </Button>
            </Link>
            <Link href="/employees" className="block">
              <Button variant="outline" className="w-full justify-start">
                <Users className="mr-2 h-4 w-4" />
                Kelola Karyawan
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Summary Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Ringkasan Hari Ini</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-700">{stats.today.present}</p>
              <p className="text-sm text-green-600">Hadir</p>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <p className="text-2xl font-bold text-yellow-700">{stats.today.late}</p>
              <p className="text-sm text-yellow-600">Terlambat</p>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <p className="text-2xl font-bold text-red-700">{stats.today.absent}</p>
              <p className="text-sm text-red-600">Tidak Hadir</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-700">{attendanceRate}%</p>
              <p className="text-sm text-blue-600">Tingkat Kehadiran</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
