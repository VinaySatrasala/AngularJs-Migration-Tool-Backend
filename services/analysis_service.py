from pathlib import Path
from typing import Dict, Any
import asyncio
from .project_analyser import AngularProjectAnalyzer

class AnalysisService:
    """Service to manage project analysis tasks"""
    
    @staticmethod
    async def analyze_project(project_path: str) -> Dict[str, Any]:
        """
        Analyze a project at the given path and return the analysis results
        """
        # Create analyzer instance
        analyzer = AngularProjectAnalyzer(
            project_path=project_path,
            output_file=str(Path(project_path) / "analysis.json")
        )
        
        # Run analysis
        results = await analyzer.analyze_project()
        return results

    @staticmethod
    async def start_analysis(project_path: str) -> None:
        """
        Start project analysis in the background
        """
        # Create task to run analysis asynchronously
        asyncio.create_task(AnalysisService.analyze_project(project_path))
