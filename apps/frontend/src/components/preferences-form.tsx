'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
    Loader2, Save, Sparkles, Briefcase, MapPin, DollarSign,
    Building2, GraduationCap, CheckCircle2, X, Plus, FileText
} from 'lucide-react';

import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

// ── Tag Input Component ──────────────────────────────────────────────
function TagInput({
    tags, onAdd, onRemove, placeholder, suggestions
}: {
    tags: string[];
    onAdd: (tag: string) => void;
    onRemove: (tag: string) => void;
    placeholder?: string;
    suggestions?: string[];
}) {
    const [input, setInput] = useState('');
    const [showSuggestions, setShowSuggestions] = useState(false);

    const filteredSuggestions = suggestions?.filter(
        s => s.toLowerCase().includes(input.toLowerCase()) && !tags.includes(s)
    ) || [];

    const handleAdd = (value: string) => {
        const trimmed = value.trim();
        if (trimmed && !tags.includes(trimmed)) {
            onAdd(trimmed);
            setInput('');
            setShowSuggestions(false);
        }
    };

    return (
        <div className="space-y-2">
            <div className="flex flex-wrap gap-2 min-h-[32px]">
                {tags.map(tag => (
                    <Badge key={tag} variant="secondary" className="flex items-center gap-1 px-3 py-1">
                        {tag}
                        <X
                            className="h-3 w-3 cursor-pointer hover:text-red-500 transition-colors"
                            onClick={() => onRemove(tag)}
                        />
                    </Badge>
                ))}
            </div>
            <div className="relative">
                <Input
                    value={input}
                    onChange={(e) => {
                        setInput(e.target.value);
                        setShowSuggestions(true);
                    }}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            handleAdd(input);
                        }
                    }}
                    onFocus={() => setShowSuggestions(true)}
                    onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                    placeholder={placeholder || 'Type and press Enter...'}
                />
                {showSuggestions && filteredSuggestions.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg max-h-40 overflow-y-auto">
                        {filteredSuggestions.slice(0, 8).map(s => (
                            <button
                                key={s}
                                type="button"
                                className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 transition-colors"
                                onMouseDown={() => handleAdd(s)}
                            >
                                {s}
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

// ── Checkbox Group ───────────────────────────────────────────────────
function CheckboxGroup({
    options, selected, onChange
}: {
    options: { value: string; label: string }[];
    selected: string[];
    onChange: (selected: string[]) => void;
}) {
    const toggle = (value: string) => {
        if (selected.includes(value)) {
            onChange(selected.filter(s => s !== value));
        } else {
            onChange([...selected, value]);
        }
    };

    return (
        <div className="flex flex-wrap gap-2">
            {options.map(opt => (
                <button
                    key={opt.value}
                    type="button"
                    onClick={() => toggle(opt.value)}
                    className={`px-4 py-2 rounded-lg border text-sm font-medium transition-all ${selected.includes(opt.value)
                            ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                            : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                        }`}
                >
                    {opt.label}
                </button>
            ))}
        </div>
    );
}

// ── Constants ────────────────────────────────────────────────────────
const WORK_MODELS = [
    { value: 'Remoto', label: '🏠 Remoto' },
    { value: 'Híbrido', label: '🔄 Híbrido' },
    { value: 'Presencial', label: '🏢 Presencial' },
];

const EMPLOYMENT_TYPES = [
    { value: 'CLT', label: 'CLT' },
    { value: 'PJ', label: 'PJ' },
    { value: 'Freelance', label: 'Freelance' },
    { value: 'Estágio', label: 'Estágio' },
];

const COMPANY_STYLES = [
    { value: 'Startup', label: '🚀 Startup' },
    { value: 'Scale-up', label: '📈 Scale-up' },
    { value: 'Big Tech', label: '🏛️ Big Tech' },
    { value: 'Consultoria', label: '💼 Consultoria' },
    { value: 'Produto', label: '📦 Produto' },
    { value: 'Agência', label: '🎨 Agência' },
];

const SENIORITY_LEVELS = [
    { value: 'Estagiário', label: 'Estagiário' },
    { value: 'Junior', label: 'Júnior' },
    { value: 'Pleno', label: 'Pleno' },
    { value: 'Senior', label: 'Sênior' },
    { value: 'Lead/Staff', label: 'Lead / Staff' },
    { value: 'Manager', label: 'Manager' },
];

const STATUS_OPTIONS = [
    { value: 'employed_looking', label: 'Empregado, buscando' },
    { value: 'unemployed', label: 'Disponível' },
    { value: 'freelancing', label: 'Freelancer' },
    { value: 'student', label: 'Estudante' },
];

const TECH_SUGGESTIONS = [
    'Python', 'JavaScript', 'TypeScript', 'React', 'Next.js', 'Node.js',
    'Java', 'C#', '.NET', 'Go', 'Rust', 'PHP', 'Ruby', 'Swift', 'Kotlin',
    'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform',
    'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
    'FastAPI', 'Django', 'Flask', 'Spring Boot', 'Express',
    'Vue.js', 'Angular', 'Svelte', 'Tailwind CSS',
    'Git', 'CI/CD', 'Linux', 'GraphQL', 'REST API',
];

// ── Main Component ───────────────────────────────────────────────────
export default function PreferencesForm({ onSaved }: { onSaved?: () => void }) {
    const queryClient = useQueryClient();

    // State
    const [technologies, setTechnologies] = useState<string[]>([]);
    const [jobTitles, setJobTitles] = useState<string[]>([]);
    const [workModels, setWorkModels] = useState<string[]>([]);
    const [employmentTypes, setEmploymentTypes] = useState<string[]>([]);
    const [companyStyles, setCompanyStyles] = useState<string[]>([]);
    const [seniorityLevel, setSeniorityLevel] = useState('');
    const [preferredLocations, setPreferredLocations] = useState<string[]>([]);
    const [salaryMin, setSalaryMin] = useState('');
    const [salaryMax, setSalaryMax] = useState('');
    const [benefits, setBenefits] = useState<string[]>([]);
    const [industries, setIndustries] = useState<string[]>([]);
    const [currentStatus, setCurrentStatus] = useState('');
    const [reasonForSearch, setReasonForSearch] = useState('');
    const [openToRelocation, setOpenToRelocation] = useState(false);
    const [availability, setAvailability] = useState('');

    const [successMessage, setSuccessMessage] = useState('');
    const [prefillLoading, setPrefillLoading] = useState(false);

    // Fetch current preferences
    const { data: userData, isLoading: userLoading } = useQuery({
        queryKey: ['user-preferences-form'],
        queryFn: async () => {
            const res = await api.get('/auth/me');
            return res.data;
        },
    });

    // Load existing preferences into state
    useEffect(() => {
        if (userData) {
            const parse = (val: any) => {
                if (!val) return [];
                if (Array.isArray(val)) return val;
                try { return JSON.parse(val); } catch { return []; }
            };
            setTechnologies(parse(userData.technologies));
            setJobTitles(parse(userData.job_titles));
            setWorkModels(parse(userData.work_models));
            setEmploymentTypes(parse(userData.employment_types));
            setCompanyStyles(parse(userData.company_styles));
            setSeniorityLevel(userData.seniority_level || '');
            setPreferredLocations(parse(userData.preferred_locations));
            setSalaryMin(userData.salary_min?.toString() || '');
            setSalaryMax(userData.salary_max?.toString() || '');
            setBenefits(parse(userData.benefits));
            setIndustries(parse(userData.industries));
            setCurrentStatus(userData.current_status || '');
            setReasonForSearch(userData.reason_for_search || '');
            setOpenToRelocation(userData.open_to_relocation || false);
            setAvailability(userData.availability || '');
        }
    }, [userData]);

    // Pre-fill from resume
    const handlePrefill = async () => {
        setPrefillLoading(true);
        try {
            const res = await api.get('/users/me/preferences/suggestions');
            const data = res.data;

            if (!data.has_resume) {
                alert('Nenhum currículo analisado encontrado. Faça upload e análise do seu currículo primeiro.');
                return;
            }

            const s = data.suggestions;
            if (s.technologies?.length) setTechnologies(prev => [...new Set([...prev, ...s.technologies])]);
            if (s.job_titles?.length) setJobTitles(prev => [...new Set([...prev, ...s.job_titles])]);
            if (s.seniority_level) setSeniorityLevel(s.seniority_level);

            setSuccessMessage(`✨ Dados do currículo "${data.resume_filename}" carregados com sucesso!`);
            setTimeout(() => setSuccessMessage(''), 4000);
        } catch (err) {
            alert('Erro ao carregar sugestões do currículo.');
        } finally {
            setPrefillLoading(false);
        }
    };

    // Save preferences
    const saveMutation = useMutation({
        mutationFn: async () => {
            const payload: Record<string, any> = {
                technologies,
                job_titles: jobTitles,
                work_models: workModels,
                employment_types: employmentTypes,
                company_styles: companyStyles,
                seniority_level: seniorityLevel || undefined,
                preferred_locations: preferredLocations,
                salary_min: salaryMin ? parseInt(salaryMin) : undefined,
                salary_max: salaryMax ? parseInt(salaryMax) : undefined,
                benefits,
                industries,
                current_status: currentStatus || undefined,
                reason_for_search: reasonForSearch || undefined,
                open_to_relocation: openToRelocation,
                availability: availability || undefined,
            };
            const res = await api.put('/users/me/preferences', payload);
            return res.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['user-preferences'] });
            queryClient.invalidateQueries({ queryKey: ['recommended-jobs'] });
            setSuccessMessage('✅ Preferências salvas com sucesso!');
            setTimeout(() => setSuccessMessage(''), 3000);
            onSaved?.();
        },
    });

    if (userLoading) {
        return (
            <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">🎯 Preferências de Vagas</h2>
                    <p className="text-sm text-gray-500 mt-1">
                        Configure suas preferências para receber recomendações personalizadas
                    </p>
                </div>
                <div className="flex gap-2">
                    <Button
                        type="button"
                        variant="outline"
                        onClick={handlePrefill}
                        disabled={prefillLoading}
                    >
                        {prefillLoading ? (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                            <Sparkles className="mr-2 h-4 w-4" />
                        )}
                        Preencher do Currículo
                    </Button>
                    <Button
                        onClick={() => saveMutation.mutate()}
                        disabled={saveMutation.isPending}
                    >
                        {saveMutation.isPending ? (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                            <Save className="mr-2 h-4 w-4" />
                        )}
                        Salvar Preferências
                    </Button>
                </div>
            </div>

            {/* Success / Error */}
            {successMessage && (
                <div className="bg-green-50 border border-green-300 text-green-800 px-4 py-3 rounded-lg flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4" />
                    {successMessage}
                </div>
            )}

            {saveMutation.isError && (
                <div className="bg-red-50 border border-red-300 text-red-800 px-4 py-3 rounded-lg">
                    Erro ao salvar preferências. Tente novamente.
                </div>
            )}

            {/* 1. Cargo & Senioridade */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Briefcase className="h-5 w-5 text-blue-600" />
                        Cargo & Senioridade
                    </CardTitle>
                    <CardDescription>Quais cargos você busca e qual seu nível de experiência?</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <Label className="mb-2 block">Cargos de Interesse</Label>
                        <TagInput
                            tags={jobTitles}
                            onAdd={(t) => setJobTitles([...jobTitles, t])}
                            onRemove={(t) => setJobTitles(jobTitles.filter(j => j !== t))}
                            placeholder="Ex: Fullstack Developer, Backend Engineer..."
                            suggestions={['Frontend Developer', 'Backend Developer', 'Fullstack Developer', 'DevOps Engineer', 'Data Engineer', 'Mobile Developer', 'Tech Lead', 'Software Engineer', 'Cloud Engineer']}
                        />
                    </div>
                    <Separator />
                    <div>
                        <Label className="mb-2 block">Nível de Senioridade</Label>
                        <CheckboxGroup
                            options={SENIORITY_LEVELS}
                            selected={seniorityLevel ? [seniorityLevel] : []}
                            onChange={(s) => setSeniorityLevel(s[s.length - 1] || '')}
                        />
                    </div>
                </CardContent>
            </Card>

            {/* 2. Tecnologias */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <GraduationCap className="h-5 w-5 text-purple-600" />
                        Tecnologias
                    </CardTitle>
                    <CardDescription>Quais tecnologias você domina ou deseja trabalhar?</CardDescription>
                </CardHeader>
                <CardContent>
                    <TagInput
                        tags={technologies}
                        onAdd={(t) => setTechnologies([...technologies, t])}
                        onRemove={(t) => setTechnologies(technologies.filter(x => x !== t))}
                        placeholder="Ex: Python, React, AWS..."
                        suggestions={TECH_SUGGESTIONS}
                    />
                </CardContent>
            </Card>

            {/* 3. Modelo de Trabalho */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Building2 className="h-5 w-5 text-green-600" />
                        Modelo de Trabalho & Empresa
                    </CardTitle>
                    <CardDescription>Como e onde você quer trabalhar?</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <Label className="mb-2 block">Modelo de Trabalho</Label>
                        <CheckboxGroup
                            options={WORK_MODELS}
                            selected={workModels}
                            onChange={setWorkModels}
                        />
                    </div>
                    <Separator />
                    <div>
                        <Label className="mb-2 block">Tipo de Contrato</Label>
                        <CheckboxGroup
                            options={EMPLOYMENT_TYPES}
                            selected={employmentTypes}
                            onChange={setEmploymentTypes}
                        />
                    </div>
                    <Separator />
                    <div>
                        <Label className="mb-2 block">Estilo de Empresa</Label>
                        <CheckboxGroup
                            options={COMPANY_STYLES}
                            selected={companyStyles}
                            onChange={setCompanyStyles}
                        />
                    </div>
                </CardContent>
            </Card>

            {/* 4. Salário & Localização */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <DollarSign className="h-5 w-5 text-yellow-600" />
                        Salário & Localização
                    </CardTitle>
                    <CardDescription>Qual sua expectativa salarial e localizações preferidas?</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="salary_min" className="mb-2 block">Salário Mínimo (R$)</Label>
                            <Input
                                id="salary_min"
                                type="number"
                                value={salaryMin}
                                onChange={(e) => setSalaryMin(e.target.value)}
                                placeholder="Ex: 8000"
                            />
                        </div>
                        <div>
                            <Label htmlFor="salary_max" className="mb-2 block">Salário Máximo (R$)</Label>
                            <Input
                                id="salary_max"
                                type="number"
                                value={salaryMax}
                                onChange={(e) => setSalaryMax(e.target.value)}
                                placeholder="Ex: 15000"
                            />
                        </div>
                    </div>
                    <Separator />
                    <div>
                        <Label className="mb-2 block">Localizações Preferidas</Label>
                        <TagInput
                            tags={preferredLocations}
                            onAdd={(t) => setPreferredLocations([...preferredLocations, t])}
                            onRemove={(t) => setPreferredLocations(preferredLocations.filter(x => x !== t))}
                            placeholder="Ex: São Paulo, Remoto Brasil..."
                            suggestions={['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre', 'Florianópolis', 'Brasília', 'Remoto Brasil', 'Internacional']}
                        />
                    </div>
                    <Separator />
                    <div className="flex items-center gap-3">
                        <input
                            type="checkbox"
                            id="relocation"
                            checked={openToRelocation}
                            onChange={(e) => setOpenToRelocation(e.target.checked)}
                            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <Label htmlFor="relocation">Aberto a relocação</Label>
                    </div>
                </CardContent>
            </Card>

            {/* 5. Status Atual */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5 text-orange-600" />
                        Status Atual
                    </CardTitle>
                    <CardDescription>Conte-nos sobre sua situação atual</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <Label className="mb-2 block">Situação Atual</Label>
                        <CheckboxGroup
                            options={STATUS_OPTIONS}
                            selected={currentStatus ? [currentStatus] : []}
                            onChange={(s) => setCurrentStatus(s[s.length - 1] || '')}
                        />
                    </div>
                    <div>
                        <Label htmlFor="availability" className="mb-2 block">Disponibilidade</Label>
                        <Input
                            id="availability"
                            value={availability}
                            onChange={(e) => setAvailability(e.target.value)}
                            placeholder="Ex: Imediata, 2 semanas, 30 dias..."
                        />
                    </div>
                </CardContent>
            </Card>

            {/* Benefícios */}
            <Card>
                <CardHeader>
                    <CardTitle>Benefícios Desejados</CardTitle>
                    <CardDescription>Quais benefícios são importantes para você?</CardDescription>
                </CardHeader>
                <CardContent>
                    <TagInput
                        tags={benefits}
                        onAdd={(t) => setBenefits([...benefits, t])}
                        onRemove={(t) => setBenefits(benefits.filter(x => x !== t))}
                        placeholder="Ex: Plano de Saúde, VR, GymPass..."
                        suggestions={['Plano de Saúde', 'Plano Dental', 'Vale Refeição', 'Vale Alimentação', 'GymPass', 'Home Office Subsídio', 'PLR', 'Stock Options', 'Seguro de Vida', 'Educação/Cursos']}
                    />
                </CardContent>
            </Card>

            {/* Bottom Save Button */}
            <div className="flex justify-end gap-3 pb-8">
                <Button
                    size="lg"
                    onClick={() => saveMutation.mutate()}
                    disabled={saveMutation.isPending}
                >
                    {saveMutation.isPending ? (
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    ) : (
                        <Save className="mr-2 h-5 w-5" />
                    )}
                    Salvar Todas as Preferências
                </Button>
            </div>
        </div>
    );
}
