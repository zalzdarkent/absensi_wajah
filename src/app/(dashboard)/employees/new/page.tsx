"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CameraCapture } from "@/components/camera-capture";
import { ArrowLeft, Save, X } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

export default function NewEmployeePage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [capturedPhotos, setCapturedPhotos] = useState<File[]>([]);
  
  const [formData, setFormData] = useState({
    employee_code: "",
    full_name: "",
    email: "",
    phone: "",
    department: "",
    position: "",
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handlePhotoCapture = (photo: File) => {
    if (capturedPhotos.length < 5) {
      setCapturedPhotos([...capturedPhotos, photo]);
      // Remove toast notification - will show count in UI instead
    }
  };

  const removePhoto = (index: number) => {
    setCapturedPhotos(capturedPhotos.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (capturedPhotos.length < 3) {
      toast.error("Minimal 3 foto wajah diperlukan");
      return;
    }

    setIsSubmitting(true);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append("employee_code", formData.employee_code);
      formDataToSend.append("full_name", formData.full_name);
      if (formData.email) formDataToSend.append("email", formData.email);
      if (formData.phone) formDataToSend.append("phone", formData.phone);
      if (formData.department) formDataToSend.append("department", formData.department);
      if (formData.position) formDataToSend.append("position", formData.position);
      
      capturedPhotos.forEach((photo) => {
        formDataToSend.append("images", photo);
      });

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/enroll`, {
        method: "POST",
        body: formDataToSend,
      });

      const result = await response.json();

      if (response.ok && result.success) {
        toast.success("Karyawan berhasil didaftarkan!");
        router.push("/employees");
      } else {
        toast.error(result.detail || result.message || "Gagal mendaftarkan karyawan");
      }
    } catch (error) {
      console.error("Error:", error);
      toast.error("Terjadi kesalahan saat mendaftarkan karyawan");
    } finally {
      setIsSubmitting(false);
    }
  };

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
          <h1 className="text-3xl font-bold">Daftarkan Karyawan Baru</h1>
          <p className="text-muted-foreground">
            Lengkapi data karyawan dan ambil foto wajah
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid gap-6 md:grid-cols-2">
          {/* Employee Information */}
          <Card>
            <CardHeader>
              <CardTitle>Informasi Karyawan</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="employee_code">Kode Karyawan *</Label>
                <Input
                  id="employee_code"
                  name="employee_code"
                  placeholder="EMP-001"
                  value={formData.employee_code}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="full_name">Nama Lengkap *</Label>
                <Input
                  id="full_name"
                  name="full_name"
                  placeholder="John Doe"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="john@example.com"
                  value={formData.email}
                  onChange={handleInputChange}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="phone">Telepon</Label>
                <Input
                  id="phone"
                  name="phone"
                  placeholder="+62 812 3456 7890"
                  value={formData.phone}
                  onChange={handleInputChange}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="department">Department</Label>
                <Input
                  id="department"
                  name="department"
                  placeholder="Engineering"
                  value={formData.department}
                  onChange={handleInputChange}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="position">Posisi</Label>
                <Input
                  id="position"
                  name="position"
                  placeholder="Software Engineer"
                  value={formData.position}
                  onChange={handleInputChange}
                />
              </div>
            </CardContent>
          </Card>

          {/* Face Photos */}
          <Card>
            <CardHeader>
              <CardTitle>Foto Wajah (3-5 foto) *</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <CameraCapture
                onCapture={handlePhotoCapture}
                maxPhotos={5}
                capturedPhotos={capturedPhotos}
              />
              
              {capturedPhotos.length > 0 && (
                <div className="space-y-2">
                  <Label>Foto yang Diambil ({capturedPhotos.length}/5)</Label>
                  <div className="grid grid-cols-3 gap-2">
                    {capturedPhotos.map((photo, index) => (
                      <div key={index} className="relative group">
                        <div className="aspect-square bg-muted rounded-lg overflow-hidden border-2">
                          <img
                            src={URL.createObjectURL(photo)}
                            alt={`Photo ${index + 1}`}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <button
                          type="button"
                          onClick={() => removePhoto(index)}
                          className="absolute top-1 right-1 bg-destructive text-destructive-foreground rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <X className="h-3 w-3" />
                        </button>
                        <p className="text-xs text-center mt-1">Foto {index + 1}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {capturedPhotos.length < 3 && (
                <p className="text-sm text-destructive">
                  ⚠️ Minimal 3 foto wajah diperlukan
                </p>
              )}
              
              {capturedPhotos.length >= 3 && (
                <p className="text-sm text-green-600">
                  ✓ Cukup foto untuk pendaftaran
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="flex justify-end gap-4 mt-6">
          <Link href="/employees">
            <Button type="button" variant="outline">
              Batal
            </Button>
          </Link>
          <Button type="submit" disabled={isSubmitting || capturedPhotos.length < 3}>
            <Save className="mr-2 h-4 w-4" />
            {isSubmitting ? "Mendaftarkan..." : "Daftarkan Karyawan"}
          </Button>
        </div>
      </form>
    </div>
  );
}
