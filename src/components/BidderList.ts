import { bidderService } from '../services/bidderService';
import { templateService } from '../services/templateService';
import { Bidder } from '../types/tender';

export class BidderList {
  private container: HTMLElement;

  constructor(container: HTMLElement) {
    this.container = container;
    this.render();
  }

  public refresh(): void {
    this.render();
  }

  private render(): void {
    const recentBidders = bidderService.getRecentBidders();
    
    this.container.innerHTML = `
      <div class="bidder-list">
        <div class="list-header">
          <h2>Recent Bidders</h2>
          <div class="list-actions">
            <button id="refresh-list" class="btn-secondary">Refresh</button>
            <button id="export-all" class="btn-primary">Export All</button>
          </div>
        </div>
        
        ${recentBidders.length === 0 ? this.renderEmptyState() : this.renderBidders(recentBidders)}
      </div>
    `;

    this.attachEventListeners();
  }

  private renderEmptyState(): string {
    return `
      <div class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>No Recent Bidders</h3>
        <p>Add some bidders to see them appear here.</p>
      </div>
    `;
  }

  private renderBidders(bidders: Bidder[]): string {
    return `
      <div class="bidders-grid">
        ${bidders.map(bidder => this.renderBidderCard(bidder)).join('')}
      </div>
    `;
  }

  private renderBidderCard(bidder: Bidder): string {
    const statusClass = this.getStatusClass(bidder.status);
    const formattedAmount = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(bidder.bidAmount);

    return `
      <div class="bidder-card" data-bidder-id="${bidder.id}">
        <div class="bidder-header">
          <h3>${bidder.name}</h3>
          <span class="status ${statusClass}">${bidder.status}</span>
        </div>
        
        <div class="bidder-details">
          <p><strong>Company:</strong> ${bidder.company}</p>
          <p><strong>Email:</strong> ${bidder.email}</p>
          <p><strong>Phone:</strong> ${bidder.phone}</p>
          <p><strong>Bid Amount:</strong> ${formattedAmount}</p>
          <p><strong>Submitted:</strong> ${new Date(bidder.submittedAt).toLocaleDateString()}</p>
        </div>
        
        <div class="bidder-actions">
          <button class="btn-small btn-primary" onclick="window.generateSingleTemplate('${bidder.id}')">
            Generate Template
          </button>
          <button class="btn-small btn-secondary" onclick="window.updateStatus('${bidder.id}', 'approved')">
            Approve
          </button>
          <button class="btn-small btn-danger" onclick="window.updateStatus('${bidder.id}', 'rejected')">
            Reject
          </button>
        </div>
      </div>
    `;
  }

  private getStatusClass(status: string): string {
    switch (status) {
      case 'approved': return 'status-approved';
      case 'rejected': return 'status-rejected';
      default: return 'status-pending';
    }
  }

  private attachEventListeners(): void {
    const refreshBtn = this.container.querySelector('#refresh-list');
    const exportBtn = this.container.querySelector('#export-all');

    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.refresh();
        this.showMessage('Bidder list refreshed!', 'success');
      });
    }

    if (exportBtn) {
      exportBtn.addEventListener('click', () => this.exportAllBidders());
    }

    // Global functions for card actions
    (window as any).generateSingleTemplate = (bidderId: string) => {
      this.generateSingleTemplate(bidderId);
    };

    (window as any).updateStatus = (bidderId: string, status: string) => {
      this.updateBidderStatus(bidderId, status);
    };
  }

  private generateSingleTemplate(bidderId: string): void {
    try {
      const tenders = bidderService.getAllTenders();
      let targetBidder: Bidder | null = null;
      let tenderTitle = '';

      // Find the bidder across all tenders
      for (const tender of tenders) {
        const bidder = tender.bidders.find(b => b.id === bidderId);
        if (bidder) {
          targetBidder = bidder;
          tenderTitle = tender.title;
          break;
        }
      }

      if (!targetBidder) {
        this.showMessage('Bidder not found', 'error');
        return;
      }

      const template = templateService.generateBidderTemplate(targetBidder, tenderTitle);
      const filename = `bidder_${targetBidder.name.replace(/\s+/g, '_')}_${Date.now()}.csv`;
      
      templateService.downloadTemplate(template, filename);
      this.showMessage('Template generated successfully!', 'success');
    } catch (error) {
      console.error('Error generating template:', error);
      this.showMessage('Failed to generate template', 'error');
    }
  }

  private updateBidderStatus(bidderId: string, status: string): void {
    try {
      const tenders = bidderService.getAllTenders();
      let success = false;

      // Find and update bidder status across all tenders
      for (const tender of tenders) {
        if (bidderService.updateBidderStatus(tender.id, bidderId, status as any)) {
          success = true;
          break;
        }
      }

      if (success) {
        this.refresh();
        this.showMessage(`Bidder status updated to ${status}`, 'success');
      } else {
        this.showMessage('Failed to update bidder status', 'error');
      }
    } catch (error) {
      console.error('Error updating status:', error);
      this.showMessage('Failed to update bidder status', 'error');
    }
  }

  private exportAllBidders(): void {
    try {
      const recentBidders = bidderService.getRecentBidders();
      
      if (recentBidders.length === 0) {
        this.showMessage('No bidders to export', 'error');
        return;
      }

      const template = templateService.generateMultipleBiddersTemplate(recentBidders, 'All Recent Bidders');
      const filename = `all_bidders_${Date.now()}.csv`;
      
      templateService.downloadTemplate(template, filename);
      this.showMessage('All bidders exported successfully!', 'success');
    } catch (error) {
      console.error('Error exporting bidders:', error);
      this.showMessage('Failed to export bidders', 'error');
    }
  }

  private showMessage(message: string, type: 'success' | 'error'): void {
    // Remove existing messages
    const existingMessages = this.container.querySelectorAll('.temp-message');
    existingMessages.forEach(msg => msg.remove());
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `temp-message message ${type}`;
    messageDiv.textContent = message;
    
    this.container.insertBefore(messageDiv, this.container.firstChild);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
      if (messageDiv.parentNode) {
        messageDiv.parentNode.removeChild(messageDiv);
      }
    }, 3000);
  }
}