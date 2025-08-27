#!/usr/bin/env python3
"""
Bidder Manager Module
Handles bidder data retrieval, search, and management
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class BidderManager:
    """Manages bidder data and provides search functionality"""
    
    def __init__(self, database_path: str = "Attached_assets/Bidder_data/bidder_database.json"):
        self.database_path = database_path
        self.bidders = self.load_bidders()
        self.recent_bidders = self.get_recent_bidders()
    
    def load_bidders(self) -> Dict:
        """Load bidder data from JSON file"""
        try:
            if os.path.exists(self.database_path):
                with open(self.database_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Bidder database not found at {self.database_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading bidder database: {e}")
            return {}
    
    def get_recent_bidders(self, days: int = 30) -> List[Dict]:
        """Get recently used bidders (within specified days)"""
        try:
            recent = []
            cutoff_date = datetime.now()
            
            for bidder_name, bidder_data in self.bidders.items():
                last_used_str = bidder_data.get('last_used', '')
                if last_used_str:
                    try:
                        # Handle different date formats
                        if '/' in last_used_str:
                            last_used = datetime.strptime(last_used_str, '%d/%m/%Y')
                        else:
                            last_used = datetime.strptime(last_used_str, '%Y-%m-%d')
                        
                        if (cutoff_date - last_used).days <= days:
                            recent.append({
                                'name': bidder_name,
                                'address': bidder_data.get('address', ''),
                                'last_used': last_used_str,
                                'days_ago': (cutoff_date - last_used).days
                            })
                    except ValueError:
                        # Skip entries with invalid dates
                        continue
            
            # Sort by most recent first
            recent.sort(key=lambda x: x.get('days_ago', 999))
            return recent[:20]  # Return top 20 recent bidders
            
        except Exception as e:
            logger.error(f"Error getting recent bidders: {e}")
            return []
    
    def search_bidders(self, query: str, limit: int = 10) -> List[Dict]:
        """Search bidders by name or address"""
        try:
            query = query.lower().strip()
            if not query:
                return []
            
            results = []
            for bidder_name, bidder_data in self.bidders.items():
                name_match = query in bidder_name.lower()
                address_match = query in bidder_data.get('address', '').lower()
                
                if name_match or address_match:
                    results.append({
                        'name': bidder_name,
                        'address': bidder_data.get('address', ''),
                        'last_used': bidder_data.get('last_used', ''),
                        'match_type': 'name' if name_match else 'address'
                    })
            
            # Sort by relevance (name matches first, then by last used date)
            results.sort(key=lambda x: (x['match_type'] != 'name', x['last_used']))
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching bidders: {e}")
            return []
    
    def get_bidder_by_name(self, name: str) -> Optional[Dict]:
        """Get specific bidder by exact name"""
        try:
            return self.bidders.get(name, None)
        except Exception as e:
            logger.error(f"Error getting bidder by name: {e}")
            return None
    
    def get_popular_bidders(self, limit: int = 10) -> List[Dict]:
        """Get most frequently used bidders"""
        try:
            # For now, return recent bidders as popular ones
            # In a real implementation, you'd track usage frequency
            return self.recent_bidders[:limit]
        except Exception as e:
            logger.error(f"Error getting popular bidders: {e}")
            return []
    
    def get_bidders_by_location(self, location: str) -> List[Dict]:
        """Get bidders by location/city"""
        try:
            location = location.lower().strip()
            results = []
            
            for bidder_name, bidder_data in self.bidders.items():
                address = bidder_data.get('address', '').lower()
                if location in address:
                    results.append({
                        'name': bidder_name,
                        'address': bidder_data.get('address', ''),
                        'last_used': bidder_data.get('last_used', '')
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting bidders by location: {e}")
            return []
    
    def get_all_bidders(self) -> List[Dict]:
        """Get all bidders sorted by name"""
        try:
            return [
                {
                    'name': name,
                    'address': data.get('address', ''),
                    'last_used': data.get('last_used', '')
                }
                for name, data in sorted(self.bidders.items())
            ]
        except Exception as e:
            logger.error(f"Error getting all bidders: {e}")
            return []
    
    def get_bidder_suggestions(self, partial_name: str, limit: int = 5) -> List[str]:
        """Get bidder name suggestions for autocomplete"""
        try:
            partial_name = partial_name.lower().strip()
            if not partial_name:
                return []
            
            suggestions = []
            for bidder_name in self.bidders.keys():
                if bidder_name.lower().startswith(partial_name):
                    suggestions.append(bidder_name)
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error getting bidder suggestions: {e}")
            return []
    
    def get_bidder_stats(self) -> Dict:
        """Get bidder database statistics"""
        try:
            total_bidders = len(self.bidders)
            recent_count = len(self.recent_bidders)
            
            # Count by location
            locations = {}
            for bidder_data in self.bidders.values():
                address = bidder_data.get('address', '')
                if address:
                    # Extract city from address (simple approach)
                    city = address.split(',')[-1].strip() if ',' in address else address
                    locations[city] = locations.get(city, 0) + 1
            
            return {
                'total_bidders': total_bidders,
                'recent_bidders': recent_count,
                'top_locations': dict(sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5])
            }
            
        except Exception as e:
            logger.error(f"Error getting bidder stats: {e}")
            return {}

# Global bidder manager instance
bidder_manager = BidderManager()
