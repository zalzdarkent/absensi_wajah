"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Camera, X, AlertCircle } from "lucide-react";

interface CameraCaptureProps {
  onCapture: (imageFile: File) => void;
  maxPhotos?: number;
  capturedPhotos?: File[];
}

export function CameraCapture({ onCapture, maxPhotos = 5, capturedPhotos = [] }: CameraCaptureProps) {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const [error, setError] = useState<string>("");
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  useEffect(() => {
    // Set video srcObject when stream changes
    if (stream && videoRef.current) {
      console.log("Setting video srcObject in useEffect");
      videoRef.current.srcObject = stream;
      videoRef.current.play().then(() => {
        console.log("Video playing successfully");
      }).catch(err => {
        console.error("Error playing video:", err);
      });
    }
  }, [stream]);

  const startCamera = async () => {
    setError("");
    console.log("Starting camera...");
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: "user"
        }
      });
      console.log("Camera stream obtained:", mediaStream);
      setStream(mediaStream);
      setIsCapturing(true);
    } catch (error: any) {
      console.error("Error accessing camera:", error);
      let errorMessage = "Tidak dapat mengakses kamera.";
      
      if (error.name === "NotAllowedError") {
        errorMessage = "Izin kamera ditolak. Silakan berikan izin kamera di browser.";
      } else if (error.name === "NotFoundError") {
        errorMessage = "Kamera tidak ditemukan.";
      } else if (error.name === "NotReadableError") {
        errorMessage = "Kamera sedang digunakan aplikasi lain.";
      }
      
      setError(errorMessage);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
      setIsCapturing(false);
    }
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.drawImage(video, 0, 0);
        
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], `photo_${Date.now()}.jpg`, { type: "image/jpeg" });
            onCapture(file);
          }
        }, "image/jpeg", 0.95);
      }
    }
  };

  return (
    <div className="space-y-4">
      {error && (
        <div className="flex items-center gap-2 p-3 bg-destructive/10 text-destructive rounded-lg">
          <AlertCircle className="h-4 w-4" />
          <p className="text-sm">{error}</p>
        </div>
      )}
      
      {!isCapturing ? (
        <Button 
          onClick={startCamera} 
          disabled={capturedPhotos.length >= maxPhotos}
          className="w-full"
        >
          <Camera className="mr-2 h-4 w-4" />
          Buka Kamera
        </Button>
      ) : (
        <Card>
          <CardContent className="p-4">
            <div className="relative">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full rounded-lg bg-black"
                style={{ minHeight: "300px" }}
              />
              <div className="flex gap-2 mt-4">
                <Button onClick={capturePhoto} className="flex-1" disabled={!stream}>
                  <Camera className="mr-2 h-4 w-4" />
                  Ambil Foto ({capturedPhotos.length}/{maxPhotos})
                </Button>
                <Button onClick={stopCamera} variant="outline">
                  <X className="mr-2 h-4 w-4" />
                  Tutup
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}
