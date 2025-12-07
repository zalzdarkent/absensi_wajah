import { NextResponse } from 'next/server';
import pool from '@/lib/db';
import { RowDataPacket } from 'mysql2';

export async function GET() {
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
    
    // Weekly attendance trend (last 7 days)
    const [weeklyTrend] = await pool.query<RowDataPacket[]>(
      `SELECT 
        attendance_date,
        COUNT(*) as total,
        SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present,
        SUM(CASE WHEN status = 'late' THEN 1 ELSE 0 END) as late
      FROM attendance_records
      WHERE attendance_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
      GROUP BY attendance_date
      ORDER BY attendance_date ASC`
    );
    
    return NextResponse.json({
      totalEmployees: employeesCount[0].total,
      today: {
        total: todayStats[0]?.total || 0,
        present: todayStats[0]?.present || 0,
        late: todayStats[0]?.late || 0,
        absent: employeesCount[0].total - (todayStats[0]?.total || 0)
      },
      recentCheckIns: recentCheckIns,
      weeklyTrend: weeklyTrend
    });
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch statistics' },
      { status: 500 }
    );
  }
}
