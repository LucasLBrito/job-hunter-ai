import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Loader2, Briefcase, MapPin, Building2, CheckCircle, XCircle, ExternalLink, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import api from '@/lib/api';

interface Job {
    id: number;
    title: string;
    company: string;
    location?: string;
    is_remote: boolean;
    source_url: string;
    source_platform: string;
    description?: string;
    compatibility_score?: number;
    pros?: string[] | string; // JSON string or list depending on parsing
    cons?: string[] | string;
}

export function JobCard({ job, onAnalyze }: { job: Job, onAnalyze: (jobId: number) => void }) {
    const [isanalyzing, setIsAnalyzing] = useState(false);

    // Helper to parse if string
    const parseList = (data?: string[] | string) => {
        if (Array.isArray(data)) return data;
        if (typeof data === 'string') {
            try {
                return JSON.parse(data);
            } catch {
                return [];
            }
        }
        return [];
    };

    const pros = parseList(job.pros);
    const cons = parseList(job.cons);

    const handleAnalyze = async () => {
        setIsAnalyzing(true);
        await onAnalyze(job.id);
        setIsAnalyzing(false);
    };

    const getScoreColor = (score?: number) => {
        if (!score) return 'text-gray-500';
        if (score >= 80) return 'text-green-600';
        if (score >= 50) return 'text-yellow-600';
        return 'text-red-600';
    };

    return (
        <Card className="h-full flex flex-col">
            <CardHeader>
                <div className="flex justify-between items-start">
                    <div>
                        <CardTitle className="text-lg font-bold hover:text-blue-600 transition-colors">
                            <a href={job.source_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
                                {job.title} <ExternalLink className="h-4 w-4" />
                            </a>
                        </CardTitle>
                        <div className="flex items-center text-sm text-gray-500 mt-1 gap-2">
                            <Building2 className="h-3 w-3" /> {job.company}
                        </div>
                        <div className="flex items-center text-sm text-gray-500 mt-1 gap-2">
                            <MapPin className="h-3 w-3" /> {job.location || 'Unknown'}
                            {job.is_remote && <Badge variant="outline">Remote</Badge>}
                        </div>
                    </div>
                    {job.compatibility_score !== null && job.compatibility_score !== undefined && (
                        <div className="flex flex-col items-center">
                            <span className={`text-2xl font-bold ${getScoreColor(job.compatibility_score)}`}>
                                {Math.round(job.compatibility_score)}%
                            </span>
                            <span className="text-xs text-muted-foreground">Match</span>
                        </div>
                    )}
                </div>
            </CardHeader>

            <CardContent className="flex-grow space-y-4">
                {/* Analysis Results */}
                {(pros.length > 0 || cons.length > 0) ? (
                    <div className="space-y-3">
                        {pros.length > 0 && (
                            <div>
                                <h4 className="text-sm font-semibold text-green-700 flex items-center mb-1">
                                    <CheckCircle className="h-4 w-4 mr-1" /> Pros
                                </h4>
                                <ul className="text-xs space-y-1 text-gray-600 pl-5 list-disc">
                                    {pros.map((p: string, i: number) => <li key={i}>{p}</li>)}
                                </ul>
                            </div>
                        )}
                        {cons.length > 0 && (
                            <div>
                                <h4 className="text-sm font-semibold text-red-700 flex items-center mb-1">
                                    <XCircle className="h-4 w-4 mr-1" /> Cons
                                </h4>
                                <ul className="text-xs space-y-1 text-gray-600 pl-5 list-disc">
                                    {cons.map((c: string, i: number) => <li key={i}>{c}</li>)}
                                </ul>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="text-sm text-gray-500 italic">
                        {job.compatibility_score ? "Analysis complete." : "No analysis yet."}
                    </div>
                )}
            </CardContent>

            <CardFooter className="pt-2 flex gap-2">
                <Button variant="outline" className="w-full" asChild>
                    <a href={job.source_url} target="_blank" rel="noopener noreferrer">
                        Apply Now
                    </a>
                </Button>
                <Button
                    variant="secondary"
                    className="w-full"
                    onClick={handleAnalyze}
                    disabled={isanalyzing || (job.compatibility_score !== null && job.compatibility_score !== undefined)}
                >
                    {isanalyzing ? <Loader2 className="h-4 w-4 animate-spin" /> : <><Sparkles className="h-4 w-4 mr-2" /> Analyze API</>}
                </Button>
            </CardFooter>
        </Card>
    );
}
