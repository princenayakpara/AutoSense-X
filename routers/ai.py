"""
AI System Brain API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, AIPredictions, OptimizationHistory
from ai_engine import AISystemBrain
from auth import get_current_active_user, User
from pydantic import BaseModel
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from fastapi.responses import FileResponse
import io
import os
from datetime import datetime

router = APIRouter(prefix="/api/ai", tags=["AI System Brain"])

# Initialize AI engine
ai_engine = AISystemBrain()


class AutoOptimizeRequest(BaseModel):
    force: bool = False


@router.get("/predict")
async def predict_system_health(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI prediction of system health and degradation risk"""
    try:
        # Bootstrap AI if not fitted
        if not ai_engine.is_fitted:
            from database import SystemMetrics
            # Get last 50 metrics for decent fitting
            metrics = db.query(SystemMetrics).order_by(SystemMetrics.timestamp.desc()).limit(50).all()
            if metrics:
                # Convert list of objects to list of dicts
                metric_dicts = []
                for m in metrics:
                    metric_dicts.append({
                        'cpu_percent': m.cpu_percent,
                        'memory_percent': m.memory_percent,
                        'disk_percent': m.disk_percent,
                        'process_count': m.process_count,
                        'high_cpu_processes': 0, # Approximation or add column
                        'high_memory_processes': 0
                    })
                ai_engine.ensure_fitted(metric_dicts)

        prediction = ai_engine.predict_degradation_risk()
        
        # Store prediction in database
        db_prediction = AIPredictions(
            risk_score=prediction["risk_score"],
            prediction_type="overall",
            explanation=prediction["explanation"],
            recommendations="\n".join(prediction["recommendations"])
        )
        db.add(db_prediction)
        db.commit()
        
        return {
            "success": True,
            "prediction": prediction
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-optimize")
async def auto_optimize_system(
    request: AutoOptimizeRequest = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Trigger automatic system optimization"""
    try:
        if request is None:
            request = AutoOptimizeRequest()
        
        result = ai_engine.auto_optimize()
        
        # Store optimization history
        for opt_type, opt_result in result.get("results", {}).items():
            history = OptimizationHistory(
                optimization_type=opt_type,
                before_value=opt_result.get("memory_before") or opt_result.get("current_processes") or 0,
                after_value=opt_result.get("memory_after") or opt_result.get("current_processes") or 0,
                success=opt_result.get("success", False),
                details=str(opt_result)
            )
            db.add(history)
        
        db.commit()
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report")
async def generate_pdf_report(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate and download PDF optimization report"""
    try:
        # Get latest prediction
        prediction = ai_engine.predict_degradation_risk()
        
        # Get recent optimizations
        recent_optimizations = db.query(OptimizationHistory).order_by(
            OptimizationHistory.timestamp.desc()
        ).limit(10).all()
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00FFFF'),
            spaceAfter=30,
        )
        story.append(Paragraph("AutoSense X - System Health Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Report Date
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # System Health Summary
        story.append(Paragraph("System Health Summary", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        health_data = [
            ['Metric', 'Value'],
            ['Risk Score', f"{prediction['risk_score']:.1%}"],
            ['Risk Level', prediction['risk_level'].upper()],
            ['CPU Usage', f"{prediction['features'].get('cpu_percent', 0):.1f}%"],
            ['Memory Usage', f"{prediction['features'].get('memory_percent', 0):.1f}%"],
            ['Disk Usage', f"{prediction['features'].get('disk_percent', 0):.1f}%"],
        ]
        
        health_table = Table(health_data, colWidths=[3*inch, 3*inch])
        health_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#16213e')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#00FFFF')),
        ]))
        story.append(health_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Explanation
        story.append(Paragraph("Analysis", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(prediction['explanation'], styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        story.append(Paragraph("Recommendations", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        for rec in prediction['recommendations']:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Optimization History
        if recent_optimizations:
            story.append(Paragraph("Recent Optimizations", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            opt_data = [['Date', 'Type', 'Status']]
            for opt in recent_optimizations:
                opt_data.append([
                    opt.timestamp.strftime('%Y-%m-%d %H:%M'),
                    opt.optimization_type,
                    'Success' if opt.success else 'Failed'
                ])
            
            opt_table = Table(opt_data, colWidths=[2*inch, 2*inch, 2*inch])
            opt_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#16213e')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#00FFFF')),
            ]))
            story.append(opt_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Save to temp file
        temp_file = f"./temp/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.makedirs("./temp", exist_ok=True)
        
        with open(temp_file, 'wb') as f:
            f.write(buffer.getvalue())
        
        return FileResponse(
            temp_file,
            media_type='application/pdf',
            filename=f"autosense_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

