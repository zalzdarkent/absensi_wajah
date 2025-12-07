import { NextResponse } from 'next/server';
import pool from '@/lib/db';
import { RowDataPacket } from 'mysql2';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    
    // Get employee details
    const [employees] = await pool.query<RowDataPacket[]>(
      `SELECT * FROM employees WHERE employee_id = ?`,
      [id]
    );
    
    if (employees.length === 0) {
      return NextResponse.json(
        { error: 'Employee not found' },
        { status: 404 }
      );
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
    
    return NextResponse.json({
      employee: employees[0],
      photos: photos,
      attendance: attendance
    });
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch employee details' },
      { status: 500 }
    );
  }
}
