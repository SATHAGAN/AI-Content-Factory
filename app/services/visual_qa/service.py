from pathlib import Path
from app.services.visual_qa.models import VisualQAResult
class VisualQAService:
    def __init__(self,min_score=0.75): self.min_score=min_score
    def inspect(self,output_path,*,expected_duration,actual_duration=None,prompt=""):
        if not Path(output_path).is_file(): return VisualQAResult(False,0.0,("visual artifact is missing",),True)
        reasons=[]; score=1.0
        if actual_duration is not None and abs(actual_duration-expected_duration)>0.5:
            score-=0.35; reasons.append("duration drift")
        if not prompt.strip(): score-=0.2; reasons.append("empty visual prompt")
        score=max(0.0,score); passed=score>=self.min_score
        return VisualQAResult(passed,score,tuple(reasons),not passed)
