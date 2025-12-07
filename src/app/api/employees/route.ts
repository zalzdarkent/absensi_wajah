import { NextResponse } from 'next/server';
import pool from '@/lib/db';
import { RowDataPacket } from 'mysql2';

export async function GET() {
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
    
    return NextResponse.json(rows);
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch employees' },
      { status: 500 }
    );
  }
}
