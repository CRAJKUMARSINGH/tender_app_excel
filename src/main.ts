import './style.css';
import { Dashboard } from './components/Dashboard';

class TenderApp {
  private dashboard: Dashboard | null = null;

  constructor() {
    this.init();
  }

  private init(): void {
    const appContainer = document.querySelector<HTMLDivElement>('#app');
    
    if (!appContainer) {
      console.error('App container not found');
      return;
    }

    try {
      this.dashboard = new Dashboard(appContainer);
      console.log('Tender Management System initialized successfully');
    } catch (error) {
      console.error('Failed to initialize application:', error);
      this.showErrorPage(appContainer);
    }
  }

  private showErrorPage(container: HTMLElement): void {
    container.innerHTML = `
      <div class="error-page">
        <h1>Application Error</h1>
        <p>Failed to load the Tender Management System. Please refresh the page.</p>
        <button onclick="window.location.reload()" class="btn-primary">Refresh Page</button>
      </div>
    `;
  }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new TenderApp();
});

// Fallback initialization if DOMContentLoaded already fired
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new TenderApp());
} else {
  new TenderApp();
}