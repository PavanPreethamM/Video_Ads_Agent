import json
import glob
from datetime import datetime

import config

class VideoAgent:
    def __init__(self):
        pass
    def load_latest_script(self) -> dict:
        scripts_file = sorted(glob.glob("data/scripts/*.json"))
        if not scripts_file:
            raise FileNotFoundError("No scripts files found.Run agents/script_agent.py")
        latest_file = scripts_file[-1]
        print(f"Loading Script files from {latest_file}")

        with open(latest_file , "r" , encoding="utf-8") as f:
            return json.load(f)

        
    def select_best_script(self ,scripts_data : dict ,script_type : str = None) -> dict:
        scripts = scripts_data.get("scripts" , [])
        if not scripts:
            raise ValueError("No scripts found in the loaded data")

        if script_type:
            for script in scripts:
                if script.get("script_type") == script_type:
                    return script
            print(f"Script type , {script_type} not found so using the first script")
        return scripts[0]

    
    def build_production_brief(self ,script : dict ,product : str = "CrowdWisdomTrading") ->str:
        duration = script.get("duration_seconds" , 45)
        hook = script.get("visual_hook" , "")
        cta = script.get("cta" , "")
        scenes = script.get("scenes" , [])

        scene_lines = []
        for scene in scenes:
            voiceover = scene.get("voiceover" , "")
            on_screen = scene.get("on_screen_text" , "")
            scene_lines.append(f" Scene {scene.get('scene_number')} : {voiceover} (on-screen text :\"{on_screen}\")")

        scenes_block = "\n".join(scene_lines)
        brief = f"""Make a {duration}-second promotional video ad for {product}, a trading education and alerts service.

Opening visual hook (first 2 seconds must show this): {hook}

Scene-by-scene breakdown:
{scenes_block}

Closing call to action: {cta}

Style: energetic, modern, social-media-native (vertical 9:16 format for
Instagram Reels / TikTok). Use bold on-screen text overlays matching the
voiceover. Background music should build urgency and excitement.
"""
        return brief

    def save_brief(self , brief : str , script_type : str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/videos/brief_{script_type}_{timestamp}.txt"

        with open(filename , "w" , encoding="utf-8") as f:
            f.write(brief)

        print(f"Production brief saved to {filename}")
        return filename
    
def main():
    agent = VideoAgent()
    scripts_data = agent.load_latest_script()

    script = agent.select_best_script(scripts_data, script_type="pain_agitate_solve")
    brief = agent.build_production_brief(script)

    print("\n=== PRODUCTION BRIEF ===\n")
    print(brief)

    agent.save_brief(brief, script.get("script_type", "unknown"))


if __name__ == "__main__":
    main()