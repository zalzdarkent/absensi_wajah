import { NextResponse } from 'next/server';
import pool from '@/lib/db';
import { RowDataPacket } from 'mysql2';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const date = searchParams.get('date');
    const employeeId = searchParams.get('employee_id');
    const status = searchParams.get('status');
    const limit = parseInt(searchParams.get('limit') || '50');
    const offset = parseInt(searchParams.get('offset') || '0');
    
    let query = `
      SELECT 
        a.attendance_id,
        a.attendance_date,
        a.check_in_time,
        a.check_out_time,
        a.status,
        a.check_in_confidence,
        a.check_out_confidence,
        a.check_in_image_path,
        a.check_out_image_path,
        e.employee_id,
        e.employee_code,
        e.full_name,
        e.department,
        e.position
      FROM attendance_records a
      JOIN employees e ON a.employee_id = e.employee_id
      WHERE 1=1
    `;
    
    const params: any[] = [];
    
    if (date) {
      query += ` AND a.attendance_date = ?`;
      params.push(date);
    }
    
    if (employeeId) {
      query += ` AND a.employee_id = ?`;
      params.push(employeeId);
    }
    
    if (status) {
      query += ` AND a.status = ?`;
      params.push(status);
    }
    
    query += ` ORDER BY a.attendance_date DESC, a.check_in_time DESC LIMIT ? OFFSET ?`;
    params.push(limit, offset);
    
    const [rows] = await pool.query<RowDataPacket[]>(query, params);
    
    // Get total count
    let countQuery = `
      SELECT COUNT(*) as total
      FROM attendance_records a
      WHERE 1=1
    `;
    const countParams: any[] = [];
    
    if (date) {
      countQuery += ` AND a.attendance_date = ?`;
      countParams.push(date);
    }
    
    if (employeeId) {
      countQuery += ` AND a.employee_id = ?`;
      countParams.push(employeeId);
    }
    
    if (status) {
      countQuery += ` AND a.status = ?`;
      countParams.push(status);
    }
    
    const [countResult] = await pool.query<RowDataPacket[]>(countQuery, countParams);
    
    return NextResponse.json({
      data: rows,
      total: countResult[0].total,
      limit,
      offset
    });
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch attendance records' },
      { status: 500 }
    );
  }
}
