export interface Bidder {
  id: string;
  name: string;
  email: string;
  phone: string;
  company: string;
  address: string;
  bidAmount: number;
  submittedAt: Date;
  documents: string[];
  status: 'pending' | 'approved' | 'rejected';
}

export interface Tender {
  id: string;
  title: string;
  description: string;
  deadline: Date;
  estimatedValue: number;
  status: 'open' | 'closed' | 'awarded';
  createdAt: Date;
  bidders: Bidder[];
}

export interface TemplateData {
  tenderTitle: string;
  bidderName: string;
  bidAmount: number;
  submissionDate: string;
  companyName: string;
  contactInfo: string;
}