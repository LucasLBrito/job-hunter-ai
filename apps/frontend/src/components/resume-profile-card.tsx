import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Brain, Briefcase, GraduationCap, Award, CheckCircle2 } from 'lucide-react';

interface ResumeProfileCardProps {
    resume: any;
}

export function ResumeProfileCard({ resume }: ResumeProfileCardProps) {
    if (!resume) {
        return (
            <Card className="bg-muted/50 border-dashed">
                <CardHeader>
                    <CardTitle>Resume Profile</CardTitle>
                    <CardDescription>Upload and analyze a resume to see your profile insights here.</CardDescription>
                </CardHeader>
            </Card>
        );
    }

    // Parse JSON fields
    const safeParse = (json: string) => {
        try {
            return JSON.parse(json || '[]');
        } catch {
            return [];
        }
    };

    const technicalSkills = safeParse(resume.technical_skills);
    const softSkills = safeParse(resume.soft_skills);

    // Calculate a mock "Profile Strength" score based on data completeness
    let score = 0;
    if (resume.ai_summary) score += 20;
    if (technicalSkills.length > 0) score += 20;
    if (softSkills.length > 0) score += 10;
    if (resume.years_of_experience !== null) score += 10;
    if (safeParse(resume.education).length > 0) score += 20;
    if (safeParse(resume.work_experience).length > 0) score += 20;

    return (
        <Card className="border-blue-200 dark:border-blue-800 shadow-sm">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30">
                <div className="flex justify-between items-start">
                    <div>
                        <CardTitle className="text-2xl text-blue-900 dark:text-blue-100 flex items-center gap-2">
                            <Brain className="h-6 w-6 text-blue-600" />
                            Professional Profile
                        </CardTitle>
                        <CardDescription>
                            Analysis based on <strong>{resume.filename}</strong>
                        </CardDescription>
                    </div>
                    <div className="text-right">
                        <div className="text-3xl font-bold text-blue-600">{score}%</div>
                        <div className="text-xs text-muted-foreground uppercase font-semibold">Profile Strength</div>
                    </div>
                </div>
                <Progress value={score} className="h-2 mt-2" />
            </CardHeader>
            <CardContent className="space-y-6 pt-6">

                {/* Summary */}
                <div className="space-y-2">
                    <h3 className="font-semibold flex items-center gap-2 text-lg">
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                        Professional Summary
                    </h3>
                    <div className="bg-slate-50 dark:bg-slate-900 p-4 rounded-lg text-sm leading-relaxed border">
                        {resume.ai_summary || "No summary available."}
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Skills */}
                    <div className="space-y-3">
                        <h3 className="font-semibold flex items-center gap-2">
                            <Award className="h-5 w-5 text-purple-500" />
                            Skills
                        </h3>

                        <div>
                            <span className="text-xs font-medium text-muted-foreground mb-1 block">Technical</span>
                            <div className="flex flex-wrap gap-1.5">
                                {technicalSkills.length > 0 ? technicalSkills.map((skill: string, i: number) => (
                                    <Badge key={i} variant="secondary" className="bg-blue-100 text-blue-800 hover:bg-blue-200 border-none">
                                        {skill}
                                    </Badge>
                                )) : <span className="text-sm text-muted-foreground">None detected</span>}
                            </div>
                        </div>

                        <div>
                            <span className="text-xs font-medium text-muted-foreground mb-1 block">Soft Skills</span>
                            <div className="flex flex-wrap gap-1.5">
                                {softSkills.length > 0 ? softSkills.map((skill: string, i: number) => (
                                    <Badge key={i} variant="outline" className="text-green-700 border-green-200">
                                        {skill}
                                    </Badge>
                                )) : <span className="text-sm text-muted-foreground">None detected</span>}
                            </div>
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="space-y-3">
                        <h3 className="font-semibold flex items-center gap-2">
                            <Briefcase className="h-5 w-5 text-orange-500" />
                            Experience
                        </h3>
                        <div className="flex items-center gap-4 bg-orange-50 dark:bg-orange-950/20 p-4 rounded-lg border border-orange-100 dark:border-orange-900">
                            <div>
                                <div className="text-2xl font-bold text-orange-700 dark:text-orange-400">
                                    {resume.years_of_experience ?? 0}
                                </div>
                                <div className="text-xs text-orange-600 dark:text-orange-500 font-medium">YEARS EXP</div>
                            </div>
                            <div className="h-8 w-px bg-orange-200 dark:bg-orange-800" />
                            <div className="text-sm text-orange-800 dark:text-orange-300">
                                Estimated based on career history analysis.
                            </div>
                        </div>
                    </div>
                </div>

            </CardContent>
        </Card>
    );
}
