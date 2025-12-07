const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');

// Read .env manually
const envPath = path.join(__dirname, '.env');
const envContent = fs.readFileSync(envPath, 'utf-8');
const env = {};
envContent.split('\n').forEach(line => {
  const [key, value] = line.split('=');
  if (key && value) env[key.trim()] = value.trim();
});

async function checkFaceEncodings() {
  const connection = await mysql.createConnection({
    host: env.DB_HOST || 'localhost',
    user: env.DB_USER || 'root',
    password: env.DB_PASSWORD || '',
    database: env.DB_NAME || 'absen_wajah',
  });

  try {
    console.log('Checking face encodings...\n');
    
    const [encodings] = await connection.query(`
      SELECT e.employee_code, e.full_name, COUNT(fe.encoding_id) as face_count
      FROM employees e
      LEFT JOIN face_encodings fe ON e.employee_id = fe.employee_id
      GROUP BY e.employee_id, e.employee_code, e.full_name
    `);
    
    console.log('Employee Face Encodings:');
    console.table(encodings);
    
    if (encodings.length === 0 || encodings[0].face_count === 0) {
      console.log('\n❌ NO FACE ENCODINGS FOUND!');
      console.log('You need to ENROLL employees first before they can check-in/out.');
      console.log('\nTo enroll an employee:');
      console.log('1. Go to http://localhost:3000/employees/new');
      console.log('2. Fill in employee details');
      console.log('3. Take at least 3 photos of their face');
      console.log('4. Submit the form');
    }
  } finally {
    await connection.end();
  }
}

checkFaceEncodings().catch(console.error);
