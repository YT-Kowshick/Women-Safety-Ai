import { useState, useMemo } from "react";
import { TrendingUp } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { PageHeader } from "@/components/common/PageHeader";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { INDIAN_STATES, CRIME_TYPES, getCrimeTrendData, type IndianState, type CrimeType } from "@/data/mockData";

export default function CrimeTrends() {
  const [selectedState, setSelectedState] = useState<IndianState>("Delhi");
  const [selectedCrime, setSelectedCrime] = useState<CrimeType>("Rape");
  const [showMovingAvg, setShowMovingAvg] = useState(false);

  const chartData = useMemo(() => {
    return getCrimeTrendData(selectedState, selectedCrime);
  }, [selectedState, selectedCrime]);

  return (
    <MainLayout>
      <PageHeader
        title="Crime Trends"
        subtitle="Analyze crime patterns over 20 years (2001-2021)"
        icon={<TrendingUp className="w-6 h-6 text-primary-foreground" />}
      />

      {/* Controls */}
      <Card className="mb-8">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="flex-1 space-y-2">
              <label className="text-sm font-medium text-foreground">State</label>
              <Select value={selectedState} onValueChange={(value) => setSelectedState(value as IndianState)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {INDIAN_STATES.map((state) => (
                    <SelectItem key={state} value={state}>
                      {state}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex-1 space-y-2">
              <label className="text-sm font-medium text-foreground">Crime Type</label>
              <Select value={selectedCrime} onValueChange={(value) => setSelectedCrime(value as CrimeType)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CRIME_TYPES.map((crime) => (
                    <SelectItem key={crime} value={crime}>
                      {crime}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end pb-1">
              <div className="flex items-center space-x-2">
                <Switch
                  id="moving-avg"
                  checked={showMovingAvg}
                  onCheckedChange={setShowMovingAvg}
                />
                <Label htmlFor="moving-avg" className="text-sm cursor-pointer">
                  3-Year Moving Average
                </Label>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Chart */}
      <Card>
        <CardHeader>
          <CardTitle>{selectedCrime} Cases in {selectedState}</CardTitle>
          <CardDescription>
            Annual reported cases from 2001 to 2021
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis 
                  dataKey="year" 
                  stroke="hsl(var(--muted-foreground))"
                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                />
                <YAxis 
                  stroke="hsl(var(--muted-foreground))"
                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "var(--radius)",
                    color: "hsl(var(--foreground))",
                  }}
                  labelStyle={{ color: "hsl(var(--foreground))" }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="count"
                  name="Reported Cases"
                  stroke="hsl(var(--primary))"
                  strokeWidth={2}
                  dot={{ fill: "hsl(var(--primary))", r: 3 }}
                  activeDot={{ r: 6 }}
                />
                {showMovingAvg && (
                  <Line
                    type="monotone"
                    dataKey="movingAvg"
                    name="3-Year Moving Avg"
                    stroke="hsl(var(--accent))"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-3xl font-bold text-foreground">
              {Math.max(...chartData.map((d) => d.count)).toLocaleString()}
            </p>
            <p className="text-sm text-muted-foreground mt-1">Peak Reported Cases</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-3xl font-bold text-foreground">
              {Math.min(...chartData.map((d) => d.count)).toLocaleString()}
            </p>
            <p className="text-sm text-muted-foreground mt-1">Lowest Reported Cases</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-3xl font-bold text-foreground">
              {Math.round(chartData.reduce((a, b) => a + b.count, 0) / chartData.length).toLocaleString()}
            </p>
            <p className="text-sm text-muted-foreground mt-1">Average per Year</p>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
