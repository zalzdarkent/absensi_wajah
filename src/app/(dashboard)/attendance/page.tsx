"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { StatusBadge } from "@/components/status-badge";
import { CameraCapture } from "@/components/camera-capture";
import { LogIn, LogOut, Filter, Calendar } from "lucide-react";
import { format } from "date-fns";
import { id as localeId } from "date-fns/locale";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface AttendanceRecord {
  attendance_id: number;
  attendance_date: string;
  check_in_time: string;
  check_out_time: string;
  status: string;
  employee_code: string;
  full_name: string;
  department: string;
  position: string;
  check_in_confidence: number;
  check_out_confidence: number;
}

function AttendanceContent() {
  const searchParams = useSearchParams();
  const action = searchParams?.get("action");
  
  const [attendance, setAttendance] = useState<AttendanceRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCheckInDialog, setShowCheckInDialog] = useState(action === "checkin");
  const [showCheckOutDialog, setShowCheckOutDialog] = useState(action === "checkout");
  const [isProcessing, setIsProcessing] = useState(false);
  const [capturedPhoto, setCapturedPhoto] = useState<File | null>(null);
  const [filterDate, setFilterDate] = useState(new Date().toISOString().split('T')[0]);

  useEffect(() => {
    fetchAttendance();
  }, [filterDate]);

  const fetchAttendance = async () => {
    try {
      setIsLoading(true);
      const res = await fetch(
        `/api/attendance?date=${filterDate}&limit=50`
      );
      const data = await res.json();
      setAttendance(data.data || []);
    } catch (error) {
      console.error("Error fetching attendance:", error);
      toast.error("Gagal memuat data kehadiran");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCheckIn = async () => {
    if (!capturedPhoto) {
      toast.error("Silakan ambil foto terlebih dahulu");
      return;
    }

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append("image", capturedPhoto);

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/attendance/checkin`,
        {
          method: "POST",
          body: formData,
        }
      );

      const result = await res.json();

      if (res.ok && result.success) {
        toast.success(`Check-in berhasil: ${result.employee.full_name}`);
        setShowCheckInDialog(false);
        setCapturedPhoto(null);
        fetchAttendance();
      } else {
        toast.error(result.detail || result.message || "Check-in gagal");
      }
    } catch (error) {
      console.error("Error:", error);
      toast.error("Terjadi kesalahan saat check-in");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCheckOut = async () => {
    if (!capturedPhoto) {
      toast.error("Silakan ambil foto terlebih dahulu");
      return;
    }

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append("image", capturedPhoto);

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/attendance/checkout`,
        {
          method: "POST",
          body: formData,
        }
      );

      const result = await res.json();

      if (res.ok && result.success) {
        toast.success(`Check-out berhasil: ${result.employee.full_name}`);
        setShowCheckOutDialog(false);
        setCapturedPhoto(null);
        fetchAttendance();
      } else {
        toast.error(result.detail || result.message || "Check-out gagal");
      }
    } catch (error) {
      console.error("Error:", error);
      toast.error("Terjadi kesalahan saat check-out");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kehadiran</h1>
          <p className="text-muted-foreground">Kelola check-in dan check-out karyawan</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowCheckInDialog(true)}>
            <LogIn className="mr-2 h-4 w-4" />
            Check In
          </Button>
          <Button onClick={() => setShowCheckOutDialog(true)} variant="outline">
            <LogOut className="mr-2 h-4 w-4" />
            Check Out
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Daftar Kehadiran</CardTitle>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <Input
                type="date"
                value={filterDate}
                onChange={(e) => setFilterDate(e.target.value)}
                className="w-40"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-center py-8 text-muted-foreground">Memuat data...</p>
          ) : attendance.length === 0 ? (
            <p className="text-center py-8 text-muted-foreground">
              Tidak ada data kehadiran untuk tanggal ini
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3 font-medium">Karyawan</th>
                    <th className="text-left p-3 font-medium">Department</th>
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
                        <div>
                          <p className="font-medium">{record.full_name}</p>
                          <p className="text-sm text-muted-foreground">{record.employee_code}</p>
                        </div>
                      </td>
                      <td className="p-3 text-sm">{record.department || '-'}</td>
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

      {/* Check-in Dialog */}
      <Dialog open={showCheckInDialog} onOpenChange={setShowCheckInDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Check In</DialogTitle>
            <DialogDescription>
              Ambil foto wajah Anda untuk melakukan check-in
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <CameraCapture
              onCapture={(photo) => setCapturedPhoto(photo)}
              maxPhotos={1}
              capturedPhotos={capturedPhoto ? [capturedPhoto] : []}
            />
            {capturedPhoto && (
              <div className="space-y-2">
                <p className="text-sm font-medium">Foto yang diambil:</p>
                <img
                  src={URL.createObjectURL(capturedPhoto)}
                  alt="Captured"
                  className="w-full max-w-sm rounded-lg border"
                />
              </div>
            )}
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setShowCheckInDialog(false);
                  setCapturedPhoto(null);
                }}
              >
                Batal
              </Button>
              <Button onClick={handleCheckIn} disabled={!capturedPhoto || isProcessing}>
                {isProcessing ? "Memproses..." : "Check In"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Check-out Dialog */}
      <Dialog open={showCheckOutDialog} onOpenChange={setShowCheckOutDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Check Out</DialogTitle>
            <DialogDescription>
              Ambil foto wajah Anda untuk melakukan check-out
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <CameraCapture
              onCapture={(photo) => setCapturedPhoto(photo)}
              maxPhotos={1}
              capturedPhotos={capturedPhoto ? [capturedPhoto] : []}
            />
            {capturedPhoto && (
              <div className="space-y-2">
                <p className="text-sm font-medium">Foto yang diambil:</p>
                <img
                  src={URL.createObjectURL(capturedPhoto)}
                  alt="Captured"
                  className="w-full max-w-sm rounded-lg border"
                />
              </div>
            )}
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setShowCheckOutDialog(false);
                  setCapturedPhoto(null);
                }}
              >
                Batal
              </Button>
              <Button onClick={handleCheckOut} disabled={!capturedPhoto || isProcessing}>
                {isProcessing ? "Memproses..." : "Check Out"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default function AttendancePage() {
  return (
    <Suspense fallback={<div className="p-6">Loading...</div>}>
      <AttendanceContent />
    </Suspense>
  );
}
