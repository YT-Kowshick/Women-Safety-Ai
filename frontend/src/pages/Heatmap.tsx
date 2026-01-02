import { useState } from "react";
import { Map } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { PageHeader } from "@/components/common/PageHeader";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { CRIME_TYPES, getHeatmapData, type CrimeType } from "@/data/mockData";

export default function Heatmap() {
  const [selectedCrime, setSelectedCrime] = useState<CrimeType>("Rape");
  const data = getHeatmapData(selectedCrime);
  const sortedData = [...data].sort((a, b) => b.intensity - a.intensity);

  return (
    <MainLayout>
      <PageHeader title="Crime Heatmap" subtitle="Geographic crime intensity across Indian states" icon={<Map className="w-6 h-6 text-primary-foreground" />} />
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="max-w-xs space-y-2">
            <label className="text-sm font-medium">Crime Type</label>
            <Select value={selectedCrime} onValueChange={(v) => setSelectedCrime(v as CrimeType)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>{CRIME_TYPES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
        {sortedData.map((item) => (
          <Card key={item.state} className="relative overflow-hidden" style={{ background: `linear-gradient(135deg, hsl(0 ${item.intensity * 84}% ${60 - item.intensity * 30}% / 0.2), transparent)` }}>
            <CardContent className="pt-4 pb-4">
              <p className="font-medium text-sm truncate">{item.state}</p>
              <p className="text-2xl font-bold">{item.count.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">cases</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </MainLayout>
  );
}
