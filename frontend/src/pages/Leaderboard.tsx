import { Trophy } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { PageHeader } from "@/components/common/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getLeaderboardData } from "@/data/mockData";
import { cn } from "@/lib/utils";

export default function Leaderboard() {
  const data = getLeaderboardData();
  const riskColors = { Low: "text-safety-high", Medium: "text-safety-medium", High: "text-safety-low" };

  return (
    <MainLayout>
      <PageHeader title="Safety Leaderboard" subtitle="States requiring most attention (2021 data)" icon={<Trophy className="w-6 h-6 text-primary-foreground" />} />
      <Card>
        <CardHeader><CardTitle>Lowest Safety Scores</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow><TableHead className="w-16">Rank</TableHead><TableHead>State</TableHead><TableHead className="text-right">Score</TableHead><TableHead className="text-right">Risk</TableHead></TableRow>
            </TableHeader>
            <TableBody>
              {data.map((row) => (
                <TableRow key={row.state}>
                  <TableCell className="font-bold">{row.rank}</TableCell>
                  <TableCell>{row.state}</TableCell>
                  <TableCell className="text-right font-mono">{row.score}</TableCell>
                  <TableCell className={cn("text-right font-medium", riskColors[row.riskLevel])}>{row.riskLevel}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </MainLayout>
  );
}
