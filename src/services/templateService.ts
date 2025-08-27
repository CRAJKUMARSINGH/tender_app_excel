import { Bidder, TemplateData } from '../types/tender';

class TemplateService {
  // Generate Excel-compatible CSV template
  generateBidderTemplate(bidder: Bidder, tenderTitle: string): string {
    try {
      const templateData: TemplateData = {
        tenderTitle,
        bidderName: bidder.name,
        bidAmount: bidder.bidAmount,
        submissionDate: new Date(bidder.submittedAt).toLocaleDateString(),
        companyName: bidder.company,
        contactInfo: `${bidder.email} | ${bidder.phone}`
      };

      // Create CSV content that can be opened in Excel
      const csvContent = this.createCSVContent(templateData);
      return csvContent;
    } catch (error) {
      console.error('Error generating template:', error);
      throw new Error('Failed to generate template');
    }
  }

  // Generate template for multiple bidders
  generateMultipleBiddersTemplate(bidders: Bidder[], tenderTitle: string): string {
    try {
      if (!bidders || bidders.length === 0) {
        throw new Error('No bidders data available');
      }

      const headers = [
        'Bidder Name',
        'Company',
        'Email',
        'Phone',
        'Bid Amount',
        'Submission Date',
        'Status',
        'Address'
      ];

      let csvContent = headers.join(',') + '\n';

      bidders.forEach(bidder => {
        const row = [
          `"${bidder.name}"`,
          `"${bidder.company}"`,
          `"${bidder.email}"`,
          `"${bidder.phone}"`,
          bidder.bidAmount.toString(),
          `"${new Date(bidder.submittedAt).toLocaleDateString()}"`,
          `"${bidder.status}"`,
          `"${bidder.address}"`
        ];
        csvContent += row.join(',') + '\n';
      });

      return csvContent;
    } catch (error) {
      console.error('Error generating multiple bidders template:', error);
      throw new Error('Failed to generate template for multiple bidders');
    }
  }

  // Download template as file
  downloadTemplate(content: string, filename: string): void {
    try {
      const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      
      if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } else {
        throw new Error('Download not supported in this browser');
      }
    } catch (error) {
      console.error('Error downloading template:', error);
      throw new Error('Failed to download template');
    }
  }

  private createCSVContent(data: TemplateData): string {
    const content = `Tender Bidder Information
Tender Title,"${data.tenderTitle}"
Bidder Name,"${data.bidderName}"
Company,"${data.companyName}"
Contact Information,"${data.contactInfo}"
Bid Amount,${data.bidAmount}
Submission Date,"${data.submissionDate}"

Generated on,"${new Date().toLocaleString()}"`;

    return content;
  }

  // Generate Excel formula template
  generateExcelFormulas(): string {
    const formulas = `Excel Formulas for Tender Analysis

Lowest Bid,=MIN(E:E)
Highest Bid,=MAX(E:E)
Average Bid,=AVERAGE(E:E)
Total Bidders,=COUNTA(A:A)-1
Winning Margin,=MIN(E:E)-AVERAGE(E:E)

Instructions:
1. Copy the bidder data to columns A-H
2. Use these formulas in separate cells for analysis
3. Column E should contain bid amounts`;

    return formulas;
  }
}

export const templateService = new TemplateService();