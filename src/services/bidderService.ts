import { Bidder, Tender } from '../types/tender';

class BidderService {
  private storageKey = 'tender_bidders';
  private tendersKey = 'tender_data';

  // Get all bidders for a specific tender
  getBidders(tenderId: string): Bidder[] {
    try {
      const tenders = this.getTenders();
      const tender = tenders.find(t => t.id === tenderId);
      return tender?.bidders || [];
    } catch (error) {
      console.error('Error retrieving bidders:', error);
      return [];
    }
  }

  // Get recent bidders (last 10)
  getRecentBidders(): Bidder[] {
    try {
      const allTenders = this.getTenders();
      const allBidders: Bidder[] = [];
      
      allTenders.forEach(tender => {
        allBidders.push(...tender.bidders);
      });

      // Sort by submission date (most recent first) and take last 10
      return allBidders
        .sort((a, b) => new Date(b.submittedAt).getTime() - new Date(a.submittedAt).getTime())
        .slice(0, 10);
    } catch (error) {
      console.error('Error retrieving recent bidders:', error);
      return [];
    }
  }

  // Add a new bidder to a tender
  addBidder(tenderId: string, bidder: Omit<Bidder, 'id' | 'submittedAt'>): boolean {
    try {
      const tenders = this.getTenders();
      const tenderIndex = tenders.findIndex(t => t.id === tenderId);
      
      if (tenderIndex === -1) {
        throw new Error('Tender not found');
      }

      const newBidder: Bidder = {
        ...bidder,
        id: this.generateId(),
        submittedAt: new Date(),
      };

      tenders[tenderIndex].bidders.push(newBidder);
      this.saveTenders(tenders);
      
      return true;
    } catch (error) {
      console.error('Error adding bidder:', error);
      return false;
    }
  }

  // Update bidder status
  updateBidderStatus(tenderId: string, bidderId: string, status: Bidder['status']): boolean {
    try {
      const tenders = this.getTenders();
      const tender = tenders.find(t => t.id === tenderId);
      
      if (!tender) {
        throw new Error('Tender not found');
      }

      const bidder = tender.bidders.find(b => b.id === bidderId);
      if (!bidder) {
        throw new Error('Bidder not found');
      }

      bidder.status = status;
      this.saveTenders(tenders);
      
      return true;
    } catch (error) {
      console.error('Error updating bidder status:', error);
      return false;
    }
  }

  private getTenders(): Tender[] {
    try {
      const data = localStorage.getItem(this.tendersKey);
      return data ? JSON.parse(data) : this.getDefaultTenders();
    } catch (error) {
      console.error('Error parsing tender data:', error);
      return this.getDefaultTenders();
    }
  }

  private saveTenders(tenders: Tender[]): void {
    try {
      localStorage.setItem(this.tendersKey, JSON.stringify(tenders));
    } catch (error) {
      console.error('Error saving tender data:', error);
    }
  }

  private getDefaultTenders(): Tender[] {
    return [
      {
        id: '1',
        title: 'Office Building Construction',
        description: 'Construction of a 5-story office building',
        deadline: new Date('2024-12-31'),
        estimatedValue: 5000000,
        status: 'open',
        createdAt: new Date('2024-01-01'),
        bidders: []
      }
    ];
  }

  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  // Get all tenders
  getAllTenders(): Tender[] {
    return this.getTenders();
  }

  // Create new tender
  createTender(tender: Omit<Tender, 'id' | 'createdAt' | 'bidders'>): boolean {
    try {
      const tenders = this.getTenders();
      const newTender: Tender = {
        ...tender,
        id: this.generateId(),
        createdAt: new Date(),
        bidders: []
      };

      tenders.push(newTender);
      this.saveTenders(tenders);
      
      return true;
    } catch (error) {
      console.error('Error creating tender:', error);
      return false;
    }
  }
}

export const bidderService = new BidderService();