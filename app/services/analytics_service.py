from app.models.user import User
from app.models.staff import Staff
from app.models.project import Project
from app.models.payment import Payment
from app import db
from datetime import datetime, timedelta
import calendar

class AnalyticsService:
    @staticmethod
    def get_dashboard_analytics(time_range='month'):
        """Get comprehensive dashboard analytics"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            
            if time_range == 'week':
                start_date = end_date - timedelta(weeks=1)
            elif time_range == 'month':
                start_date = end_date - timedelta(days=30)
            elif time_range == 'quarter':
                start_date = end_date - timedelta(days=90)
            elif time_range == 'year':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            # User analytics
            total_users = User.query.count()
            total_staff = Staff.query.count()
            active_users = User.query.filter_by(status='active').count()
            new_users = User.query.filter(User.created_at >= start_date).count()
            
            # Project analytics
            total_projects = Project.query.count()
            projects_in_range = Project.query.filter(Project.created_at >= start_date).count()
            completed_projects = Project.query.filter_by(status='completed').count()
            completed_in_range = Project.query.filter(
                Project.status == 'completed',
                Project.completed_at >= start_date
            ).count()
            
            # Payment analytics
            total_revenue = db.session.query(db.func.sum(Payment.amount))\
                                  .filter_by(status='completed')\
                                  .scalar() or 0
            
            revenue_in_range = db.session.query(db.func.sum(Payment.amount))\
                                     .filter(
                                         Payment.status == 'completed',
                                         Payment.processed_at >= start_date
                                     )\
                                     .scalar() or 0
            
            # Calculate growth rates
            previous_period_start = start_date - timedelta(days=30)
            previous_period_end = start_date
            
            previous_users = User.query.filter(
                User.created_at >= previous_period_start,
                User.created_at < previous_period_end
            ).count()
            
            previous_projects = Project.query.filter(
                Project.created_at >= previous_period_start,
                Project.created_at < previous_period_end
            ).count()
            
            previous_revenue = db.session.query(db.func.sum(Payment.amount))\
                                     .filter(
                                         Payment.status == 'completed',
                                         Payment.processed_at >= previous_period_start,
                                         Payment.processed_at < previous_period_end
                                     )\
                                     .scalar() or 0
            
            user_growth = ((new_users - previous_users) / max(previous_users, 1)) * 100
            project_growth = ((projects_in_range - previous_projects) / max(previous_projects, 1)) * 100
            revenue_growth = ((revenue_in_range - previous_revenue) / max(previous_revenue, 1)) * 100
            
            analytics = {
                'time_range': time_range,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'users': {
                    'total': total_users,
                    'staff': total_staff,
                    'active': active_users,
                    'new_users': new_users,
                    'growth_rate': round(user_growth, 2)
                },
                'projects': {
                    'total': total_projects,
                    'new_projects': projects_in_range,
                    'completed': completed_projects,
                    'completed_in_range': completed_in_range,
                    'growth_rate': round(project_growth, 2)
                },
                'revenue': {
                    'total': float(total_revenue),
                    'period_revenue': float(revenue_in_range),
                    'growth_rate': round(revenue_growth, 2)
                }
            }
            
            return {
                'success': True,
                'analytics': analytics
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Analytics generation failed: {str(e)}'}
    
    @staticmethod
    def get_revenue_analytics(time_range='month'):
        """Get revenue analytics"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            
            if time_range == 'week':
                start_date = end_date - timedelta(weeks=1)
            elif time_range == 'month':
                start_date = end_date - timedelta(days=30)
            elif time_range == 'quarter':
                start_date = end_date - timedelta(days=90)
            elif time_range == 'year':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Revenue by status
            revenue_by_status = db.session.query(
                Payment.status,
                db.func.sum(Payment.amount).label('total'),
                db.func.count(Payment.id).label('count')
            ).filter(Payment.created_at >= start_date)\
             .group_by(Payment.status)\
             .all()
            
            status_breakdown = {}
            for status, total, count in revenue_by_status:
                status_breakdown[status] = {
                    'total': float(total) if total else 0,
                    'count': count
                }
            
            # Monthly revenue trend
            monthly_revenue = db.session.query(
                db.func.date_trunc('month', Payment.processed_at).label('month'),
                db.func.sum(Payment.amount).label('revenue')
            ).filter(
                Payment.status == 'completed',
                Payment.processed_at >= start_date
            ).group_by(db.func.date_trunc('month', Payment.processed_at))\
             .order_by(db.func.date_trunc('month', Payment.processed_at))\
             .all()
            
            revenue_trend = []
            for month, revenue in monthly_revenue:
                revenue_trend.append({
                    'month': month.strftime('%Y-%m'),
                    'revenue': float(revenue) if revenue else 0
                })
            
            # Top revenue sources (research fields)
            field_revenue = db.session.query(
                Project.research_field,
                db.func.sum(Payment.amount).label('total')
            ).join(Project, Payment.project_id == Project.id)\
             .filter(
                 Payment.status == 'completed',
                 Payment.processed_at >= start_date
             )\
             .group_by(Project.research_field)\
             .order_by(db.func.sum(Payment.amount).desc())\
             .limit(10)\
             .all()
            
            top_fields = []
            for field, total in field_revenue:
                top_fields.append({
                    'field': field,
                    'revenue': float(total) if total else 0
                })
            
            analytics = {
                'time_range': time_range,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'revenue_by_status': status_breakdown,
                'monthly_trend': revenue_trend,
                'top_research_fields': top_fields
            }
            
            return {
                'success': True,
                'analytics': analytics
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Revenue analytics failed: {str(e)}'}
    
    @staticmethod
    def get_project_analytics(time_range='month'):
        """Get project analytics"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            
            if time_range == 'week':
                start_date = end_date - timedelta(weeks=1)
            elif time_range == 'month':
                start_date = end_date - timedelta(days=30)
            elif time_range == 'quarter':
                start_date = end_date - timedelta(days=90)
            elif time_range == 'year':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Projects by status
            projects_by_status = db.session.query(
                Project.status,
                db.func.count(Project.id).label('count')
            ).filter(Project.created_at >= start_date)\
             .group_by(Project.status)\
             .all()
            
            status_breakdown = {}
            for status, count in projects_by_status:
                status_breakdown[status] = count
            
            # Projects by research field
            projects_by_field = db.session.query(
                Project.research_field,
                db.func.count(Project.id).label('count')
            ).filter(Project.created_at >= start_date)\
             .group_by(Project.research_field)\
             .order_by(db.func.count(Project.id).desc())\
             .all()
            
            field_breakdown = []
            for field, count in projects_by_field:
                field_breakdown.append({
                    'field': field,
                    'count': count
                })
            
            # Project completion rate
            total_projects = Project.query.filter(Project.created_at >= start_date).count()
            completed_projects = Project.query.filter(
                Project.created_at >= start_date,
                Project.status == 'completed'
            ).count()
            
            completion_rate = (completed_projects / max(total_projects, 1)) * 100
            
            # Average project duration
            completed_projects_with_duration = db.session.query(
                Project.completed_at,
                Project.assigned_at
            ).filter(
                Project.created_at >= start_date,
                Project.status == 'completed',
                Project.completed_at.isnot(None),
                Project.assigned_at.isnot(None)
            ).all()
            
            total_duration = 0
            project_count = len(completed_projects_with_duration)
            
            for completed_at, assigned_at in completed_projects_with_duration:
                duration = (completed_at - assigned_at).total_seconds() / 86400  # Convert to days
                total_duration += duration
            
            avg_duration = total_duration / max(project_count, 1) if project_count > 0 else 0
            
            analytics = {
                'time_range': time_range,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'projects_by_status': status_breakdown,
                'projects_by_field': field_breakdown,
                'completion_rate': round(completion_rate, 2),
                'average_duration_days': round(avg_duration, 2),
                'total_projects': total_projects,
                'completed_projects': completed_projects
            }
            
            return {
                'success': True,
                'analytics': analytics
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Project analytics failed: {str(e)}'}
    
    @staticmethod
    def get_staff_analytics(time_range='month'):
        """Get staff analytics"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            
            if time_range == 'week':
                start_date = end_date - timedelta(weeks=1)
            elif time_range == 'month':
                start_date = end_date - timedelta(days=30)
            elif time_range == 'quarter':
                start_date = end_date - timedelta(days=90)
            elif time_range == 'year':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Staff performance metrics
            staff_performance = db.session.query(
                Staff.id,
                Staff.user_id,
                Staff.total_projects,
                Staff.completed_projects,
                Staff.rating,
                Staff.specialization
            ).join(User, Staff.user_id == User.id)\
             .filter(User.role == 'staff')\
             .all()
            
            performance_data = []
            total_projects = 0
            total_completed = 0
            total_revenue = 0
            
            for staff in staff_performance:
                completion_rate = (staff.completed_projects / max(staff.total_projects, 1)) * 100
                
                # Calculate revenue for this staff member
                staff_revenue = db.session.query(db.func.sum(Payment.amount))\
                                     .join(Project, Payment.project_id == Project.id)\
                                     .filter(
                                         Project.assigned_staff_id == staff.id,
                                         Payment.status == 'completed',
                                         Payment.processed_at >= start_date
                                     )\
                                     .scalar() or 0
                
                performance_data.append({
                    'staff_id': staff.id,
                    'name': staff.user.name,
                    'specialization': staff.specialization,
                    'total_projects': staff.total_projects,
                    'completed_projects': staff.completed_projects,
                    'completion_rate': round(completion_rate, 2),
                    'rating': round(staff.rating, 2),
                    'revenue': float(staff_revenue)
                })
                
                total_projects += staff.total_projects
                total_completed += staff.completed_projects
                total_revenue += staff_revenue
            
            # Top performing staff
            top_performers = sorted(
                performance_data,
                key=lambda x: x['completion_rate'],
                reverse=True
            )[:10]
            
            # Staff by specialization
            staff_by_specialization = db.session.query(
                Staff.specialization,
                db.func.count(Staff.id).label('count')
            ).join(User, Staff.user_id == User.id)\
             .filter(User.role == 'staff')\
             .group_by(Staff.specialization)\
             .order_by(db.func.count(Staff.id).desc())\
             .all()
            
            specialization_breakdown = []
            for specialization, count in staff_by_specialization:
                specialization_breakdown.append({
                    'specialization': specialization,
                    'count': count
                })
            
            analytics = {
                'time_range': time_range,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'total_staff': len(performance_data),
                'total_projects': total_projects,
                'total_completed': total_completed,
                'total_revenue': float(total_revenue),
                'overall_completion_rate': round((total_completed / max(total_projects, 1)) * 100, 2),
                'top_performers': top_performers,
                'staff_by_specialization': specialization_breakdown
            }
            
            return {
                'success': True,
                'analytics': analytics
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Staff analytics failed: {str(e)}'}
    
    @staticmethod
    def get_user_analytics(time_range='month'):
        """Get user analytics"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            
            if time_range == 'week':
                start_date = end_date - timedelta(weeks=1)
            elif time_range == 'month':
                start_date = end_date - timedelta(days=30)
            elif time_range == 'quarter':
                start_date = end_date - timedelta(days=90)
            elif time_range == 'year':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            # User registration trends
            registration_trend = db.session.query(
                db.func.date_trunc('day', User.created_at).label('date'),
                db.func.count(User.id).label('count')
            ).filter(User.created_at >= start_date)\
             .group_by(db.func.date_trunc('day', User.created_at))\
             .order_by(db.func.date_trunc('day', User.created_at))\
             .all()
            
            user_trend = []
            for date, count in registration_trend:
                user_trend.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'registrations': count
                })
            
            # User activity metrics
            total_users = User.query.count()
            active_users = User.query.filter_by(status='active').count()
            new_users = User.query.filter(User.created_at >= start_date).count()
            
            # User by role
            users_by_role = db.session.query(
                User.role,
                db.func.count(User.id).label('count')
            ).group_by(User.role)\
             .all()
            
            role_breakdown = {}
            for role, count in users_by_role:
                role_breakdown[role] = count
            
            # User engagement (projects per user)
            user_projects = db.session.query(
                User.id,
                User.name,
                db.func.count(Project.id).label('project_count')
            ).outerjoin(Project, User.id == Project.user_id)\
             .group_by(User.id, User.name)\
             .order_by(db.func.count(Project.id).desc())\
             .limit(10)\
             .all()
            
            top_users = []
            for user_id, name, project_count in user_projects:
                top_users.append({
                    'user_id': user_id,
                    'name': name,
                    'project_count': project_count
                })
            
            analytics = {
                'time_range': time_range,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'total_users': total_users,
                'active_users': active_users,
                'new_users': new_users,
                'users_by_role': role_breakdown,
                'registration_trend': user_trend,
                'top_users': top_users
            }
            
            return {
                'success': True,
                'analytics': analytics
            }
            
        except Exception as e:
            return {'success': False, 'message': f'User analytics failed: {str(e)}'}
    
    @staticmethod
    def get_comprehensive_analytics():
        """Get comprehensive analytics for admin dashboard"""
        try:
            # Get all analytics for different time ranges
            dashboard_month = AnalyticsService.get_dashboard_analytics('month')
            dashboard_quarter = AnalyticsService.get_dashboard_analytics('quarter')
            dashboard_year = AnalyticsService.get_dashboard_analytics('year')
            
            revenue_month = AnalyticsService.get_revenue_analytics('month')
            revenue_quarter = AnalyticsService.get_revenue_analytics('quarter')
            revenue_year = AnalyticsService.get_revenue_analytics('year')
            
            project_month = AnalyticsService.get_project_analytics('month')
            project_quarter = AnalyticsService.get_project_analytics('quarter')
            project_year = AnalyticsService.get_project_analytics('year')
            
            staff_month = AnalyticsService.get_staff_analytics('month')
            staff_quarter = AnalyticsService.get_staff_analytics('quarter')
            staff_year = AnalyticsService.get_staff_analytics('year')
            
            user_month = AnalyticsService.get_user_analytics('month')
            user_quarter = AnalyticsService.get_user_analytics('quarter')
            user_year = AnalyticsService.get_user_analytics('year')
            
            return {
                'success': True,
                'analytics': {
                    'dashboard': {
                        'month': dashboard_month.get('analytics'),
                        'quarter': dashboard_quarter.get('analytics'),
                        'year': dashboard_year.get('analytics')
                    },
                    'revenue': {
                        'month': revenue_month.get('analytics'),
                        'quarter': revenue_quarter.get('analytics'),
                        'year': revenue_year.get('analytics')
                    },
                    'projects': {
                        'month': project_month.get('analytics'),
                        'quarter': project_quarter.get('analytics'),
                        'year': project_year.get('analytics')
                    },
                    'staff': {
                        'month': staff_month.get('analytics'),
                        'quarter': staff_quarter.get('analytics'),
                        'year': staff_year.get('analytics')
                    },
                    'users': {
                        'month': user_month.get('analytics'),
                        'quarter': user_quarter.get('analytics'),
                        'year': user_year.get('analytics')
                    }
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Comprehensive analytics failed: {str(e)}'}


# Create instance for direct use
analytics_service = AnalyticsService()
