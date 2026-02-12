import {
    BarChart3, Users, FileText, Calendar, DollarSign,
    Globe, FolderOpen, HardHat, ShieldCheck,
    UserCheck, Wrench, PieChart
} from 'lucide-react';

export const modules = [
    {
        id: 'command-center',
        title: 'Project Command Center',
        description: 'The central nervous system of your construction business. Get a bird’s eye view of every active job, critical alerts, and financial health in one dashboard.',
        icon: BarChart3,
        benefits: ['Real-time project tracking', 'Critical path alerts', 'Unified communication feed']
    },
    {
        id: 'crm',
        title: 'CRM & Lead Management',
        description: 'Stop losing leads in spreadsheets. Track every opportunity from initial contact to contract signature with automated follow-ups.',
        icon: Users,
        benefits: ['Automated lead capture', 'Pipeline visualization', 'Client communication logs']
    },
    {
        id: 'estimating',
        title: 'Estimating & Takeoff',
        description: 'Build accurate estimates in minutes, not hours. Integrated digital takeoffs ensuring you never underbid a project again.',
        icon: FileText,
        benefits: [' digital takeoffs', 'Cost database integration', 'One-click proposal generation']
    },
    {
        id: 'scheduling',
        title: 'Scheduling & Resource Management',
        description: 'Dynamic Gantt charts that actually work for construction. Drag-and-drop scheduling that automatically adjusts dependent tasks.',
        icon: Calendar,
        benefits: ['Critical path management', 'Resource allocation', 'Delay impact analysis']
    },
    {
        id: 'financials',
        title: 'Financial Management',
        description: 'Real-time job costing that integrates with QuickBooks. Know exactly where you stand on profit margins before the job is done.',
        icon: DollarSign,
        benefits: ['WIP reporting', 'AIA billing support', 'Change order management']
    },
    {
        id: 'client-portal',
        title: 'Client Collaboration Portal',
        description: 'Give your clients a professional experience. Share photos, documents, and daily logs in a branded portal they can access anywhere.',
        icon: Globe,
        benefits: ['Selection approvals', 'Progress photos', 'Transparent communication']
    },
    {
        id: 'documents',
        title: 'Document & Photo Control',
        description: 'Unlimited storage for plans, permits, and photos. Organized by project and accessible from the field mobile app.',
        icon: FolderOpen,
        benefits: ['Version control', 'Mobile uploads', 'Plan markup tools']
    },
    {
        id: 'field-ops',
        title: 'Field Operations Hub',
        description: 'Empower your superintendents. Mobile-first tools for daily logs, time tracking, and site issues.',
        icon: HardHat,
        benefits: ['Daily construction reports', 'GPS time clock', 'Weather tracking']
    },
    {
        id: 'quality-safety',
        title: 'Quality & Safety Compliance',
        description: 'Standardize your quality control and safety inspections. Reduce risk and ensure every job meets your high standards.',
        icon: ShieldCheck,
        benefits: ['Customizable checklists', 'Safety toolbox talks', 'Incident reporting']
    },
    {
        id: 'payroll',
        title: 'Payroll & Workforce',
        description: 'Streamline payroll for the construction industry. Handle certified payroll, prevailing wages, and union reports with ease.',
        icon: UserCheck,
        benefits: ['Certified payroll reports', 'Union compliance', 'Labor burden tracking']
    },
    {
        id: 'service',
        title: 'Service & Warranty',
        description: 'Turn finished projects into long-term relationships. Manage warranty claims and service work orders efficiently.',
        icon: Wrench,
        benefits: ['Warranty tracking', 'Service dispatching', 'Maintenance contracts']
    },
    {
        id: 'analytics',
        title: 'Analytics & Reporting',
        description: 'Turn data into decisions. Customized reports on profitability, productivity, and business growth metrics.',
        icon: PieChart,
        benefits: ['Custom report builder', 'Profitability analysis', 'Forecasting tools']
    }
];
