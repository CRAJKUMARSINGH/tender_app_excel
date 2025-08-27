import { BidderForm } from './BidderForm';
import { BidderList } from './BidderList';
import { bidderService } from '../services/bidderService';

export class Dashboard {
  private container: HTMLElement;
  private bidderList: BidderList | null = null;

  constructor(container: HTMLElement) {
    this.container = container;
    this.render();
  }

  private render(): void {
    this.container.innerHTML = `
      <div class="dashboard">
        <header class="dashboard-header">
          <h1>Tender Management System</h1>
          <div class="stats">
            <div class="stat-card">
              <span class="stat-number">${this.getTotalBidders()}</span>
              <span class="stat-label">Total Bidders</span>
            </div>
            <div class="stat-card">
              <span class="stat-number">${this.getActiveTenders()}</span>
              <span class="stat-label">Active Tenders</span>
            </div>
            <div class="stat-card">
              <span class="stat-number">${this.getPendingBids()}</span>
              <span class="stat-label">Pending Bids</span>
            </div>
          </div>
        </header>

        <div class="dashboard-content">
          <div class="left-panel">
            <div id="bidder-form-container"></div>
          </div>
          
          <div class="right-panel">
            <div id="bidder-list-container"></div>
          </div>
        </div>
      </div>
    `;

    this.initializeComponents();
  }

  private initializeComponents(): void {
    const formContainer = this.container.querySelector('#bidder-form-container') as HTMLElement;
    const listContainer = this.container.querySelector('#bidder-list-container') as HTMLElement;

    if (formContainer && listContainer) {
      // Initialize bidder list first
      this.bidderList = new BidderList(listContainer);
      
      // Initialize form with callback to refresh list
      new BidderForm(formContainer, () => {
        if (this.bidderList) {
          this.bidderList.refresh();
        }
        this.updateStats();
      });
    }
  }

  private updateStats(): void {
    const statNumbers = this.container.querySelectorAll('.stat-number');
    if (statNumbers.length >= 3) {
      statNumbers[0].textContent = this.getTotalBidders().toString();
      statNumbers[1].textContent = this.getActiveTenders().toString();
      statNumbers[2].textContent = this.getPendingBids().toString();
    }
  }

  private getTotalBidders(): number {
    const tenders = bidderService.getAllTenders();
    return tenders.reduce((total, tender) => total + tender.bidders.length, 0);
  }

  private getActiveTenders(): number {
    const tenders = bidderService.getAllTenders();
    return tenders.filter(tender => tender.status === 'open').length;
  }

  private getPendingBids(): number {
    const tenders = bidderService.getAllTenders();
    let pendingCount = 0;
    
    tenders.forEach(tender => {
      pendingCount += tender.bidders.filter(bidder => bidder.status === 'pending').length;
    });
    
    return pendingCount;
  }
}