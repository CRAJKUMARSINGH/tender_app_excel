import { bidderService } from '../services/bidderService';
import { templateService } from '../services/templateService';

export class BidderForm {
  private container: HTMLElement;
  private onBidderAdded: () => void;

  constructor(container: HTMLElement, onBidderAdded: () => void) {
    this.container = container;
    this.onBidderAdded = onBidderAdded;
    this.render();
  }

  private render(): void {
    this.container.innerHTML = `
      <div class="bidder-form">
        <h2>Add New Bidder</h2>
        <form id="bidder-form" class="form-grid">
          <div class="form-group">
            <label for="bidder-name">Bidder Name *</label>
            <input type="text" id="bidder-name" required>
          </div>
          
          <div class="form-group">
            <label for="company">Company *</label>
            <input type="text" id="company" required>
          </div>
          
          <div class="form-group">
            <label for="email">Email *</label>
            <input type="email" id="email" required>
          </div>
          
          <div class="form-group">
            <label for="phone">Phone *</label>
            <input type="tel" id="phone" required>
          </div>
          
          <div class="form-group">
            <label for="address">Address</label>
            <textarea id="address" rows="3"></textarea>
          </div>
          
          <div class="form-group">
            <label for="bid-amount">Bid Amount *</label>
            <input type="number" id="bid-amount" step="0.01" min="0" required>
          </div>
          
          <div class="form-actions">
            <button type="submit" class="btn-primary">Add Bidder</button>
            <button type="button" id="clear-form" class="btn-secondary">Clear</button>
          </div>
        </form>
      </div>
    `;

    this.attachEventListeners();
  }

  private attachEventListeners(): void {
    const form = this.container.querySelector('#bidder-form') as HTMLFormElement;
    const clearBtn = this.container.querySelector('#clear-form') as HTMLButtonElement;

    if (form) {
      form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', () => this.clearForm());
    }
  }

  private handleSubmit(e: Event): void {
    e.preventDefault();
    
    try {
      const formData = this.getFormData();
      
      // Validate required fields
      if (!this.validateForm(formData)) {
        return;
      }

      // Add bidder to the first available tender (in a real app, you'd select the tender)
      const tenders = bidderService.getAllTenders();
      if (tenders.length === 0) {
        this.showError('No tenders available. Please create a tender first.');
        return;
      }

      const success = bidderService.addBidder(tenders[0].id, {
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        company: formData.company,
        address: formData.address,
        bidAmount: formData.bidAmount,
        documents: [],
        status: 'pending'
      });

      if (success) {
        this.showSuccess('Bidder added successfully!');
        this.clearForm();
        this.onBidderAdded();
        
        // Auto-generate template after successful submission
        this.generateTemplate(formData, tenders[0].title);
      } else {
        this.showError('Failed to add bidder. Please try again.');
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      this.showError('An error occurred while adding the bidder.');
    }
  }

  private getFormData() {
    const getName = () => (this.container.querySelector('#bidder-name') as HTMLInputElement)?.value?.trim() || '';
    const getCompany = () => (this.container.querySelector('#company') as HTMLInputElement)?.value?.trim() || '';
    const getEmail = () => (this.container.querySelector('#email') as HTMLInputElement)?.value?.trim() || '';
    const getPhone = () => (this.container.querySelector('#phone') as HTMLInputElement)?.value?.trim() || '';
    const getAddress = () => (this.container.querySelector('#address') as HTMLTextAreaElement)?.value?.trim() || '';
    const getBidAmount = () => parseFloat((this.container.querySelector('#bid-amount') as HTMLInputElement)?.value || '0');

    return {
      name: getName(),
      company: getCompany(),
      email: getEmail(),
      phone: getPhone(),
      address: getAddress(),
      bidAmount: getBidAmount()
    };
  }

  private validateForm(data: any): boolean {
    if (!data.name) {
      this.showError('Bidder name is required');
      return false;
    }
    if (!data.company) {
      this.showError('Company name is required');
      return false;
    }
    if (!data.email || !this.isValidEmail(data.email)) {
      this.showError('Valid email is required');
      return false;
    }
    if (!data.phone) {
      this.showError('Phone number is required');
      return false;
    }
    if (!data.bidAmount || data.bidAmount <= 0) {
      this.showError('Valid bid amount is required');
      return false;
    }
    return true;
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  private generateTemplate(bidderData: any, tenderTitle: string): void {
    try {
      const bidder: Bidder = {
        id: 'temp',
        name: bidderData.name,
        email: bidderData.email,
        phone: bidderData.phone,
        company: bidderData.company,
        address: bidderData.address,
        bidAmount: bidderData.bidAmount,
        submittedAt: new Date(),
        documents: [],
        status: 'pending'
      };

      const template = templateService.generateBidderTemplate(bidder, tenderTitle);
      const filename = `bidder_${bidderData.name.replace(/\s+/g, '_')}_${Date.now()}.csv`;
      
      templateService.downloadTemplate(template, filename);
      this.showSuccess('Template generated and downloaded successfully!');
    } catch (error) {
      console.error('Error generating template:', error);
      this.showError('Failed to generate template');
    }
  }

  private clearForm(): void {
    const form = this.container.querySelector('#bidder-form') as HTMLFormElement;
    if (form) {
      form.reset();
    }
    this.clearMessages();
  }

  private showSuccess(message: string): void {
    this.showMessage(message, 'success');
  }

  private showError(message: string): void {
    this.showMessage(message, 'error');
  }

  private showMessage(message: string, type: 'success' | 'error'): void {
    this.clearMessages();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    const form = this.container.querySelector('#bidder-form');
    if (form) {
      form.insertBefore(messageDiv, form.firstChild);
      
      // Auto-remove message after 5 seconds
      setTimeout(() => {
        if (messageDiv.parentNode) {
          messageDiv.parentNode.removeChild(messageDiv);
        }
      }, 5000);
    }
  }

  private clearMessages(): void {
    const messages = this.container.querySelectorAll('.message');
    messages.forEach(msg => msg.remove());
  }
}