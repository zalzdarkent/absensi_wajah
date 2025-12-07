import { Badge } from "@/components/ui/badge";

interface StatusBadgeProps {
  status: string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const variants: Record<string, { variant: "default" | "secondary" | "destructive" | "outline"; label: string }> = {
    present: { variant: "default", label: "Hadir" },
    late: { variant: "secondary", label: "Terlambat" },
    absent: { variant: "destructive", label: "Tidak Hadir" },
    half_day: { variant: "outline", label: "Setengah Hari" },
    on_leave: { variant: "outline", label: "Cuti" },
    active: { variant: "default", label: "Aktif" },
    inactive: { variant: "secondary", label: "Tidak Aktif" },
    suspended: { variant: "destructive", label: "Suspended" },
  };

  const config = variants[status.toLowerCase()] || { variant: "outline" as const, label: status };

  return <Badge variant={config.variant}>{config.label}</Badge>;
}
