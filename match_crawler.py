import requests
import json
import os
import time
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


FOOTBALL_API_KEY = "3eed7e6d5ac74a4ba7f1089d0245809b"  
API_BASE_URL = "https://api.football-data.org/v4"
REQUEST_DELAY = 2  


def get_internal_data_dir():
    
    current_script_path = os.path.abspath(__file__)
   
    datacrawler_dir = os.path.dirname(current_script_path)
    
    project_root_dir = os.path.dirname(datacrawler_dir)
  
    internal_data_dir = os.path.join(project_root_dir, "data")

    os.makedirs(internal_data_dir, exist_ok=True)
    return internal_data_dir

def main():
 
    session = requests.Session()
    retry_strategy = Retry(
        total=3, 
        backoff_factor=1,  
        status_forcelist=[429, 500, 502, 503, 504],  
        allowed_methods=["GET"]
    )
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}

 
 
    try:
        standings_url = f"{API_BASE_URL}/competitions/PL/standings"
        standings_resp = session.get(standings_url, headers=headers, timeout=30)
        standings_resp.raise_for_status()
        standings_data = standings_resp.json()["standings"][0]["table"]
        
    
        data_dir = get_internal_data_dir()
        today = datetime.now().strftime("%Y-%m-%d")
        standings_filename = os.path.join(data_dir, f"match_data_{today}.txt")
        with open(standings_filename, "w", encoding="utf-8") as f:
            f.write("排名,球队名称,比赛场次,胜场,平场,负场,积分\n")
            for team_entry in standings_data:
                rank = team_entry["position"]
                team_name = team_entry["team"]["name"]
                played = team_entry["playedGames"]
                won = team_entry["won"]
                draw = team_entry["draw"]
                lost = team_entry["lost"]
                points = team_entry["points"]
                f.write(f"{rank},{team_name},{played},{won},{draw},{lost},{points}\n")
        print(f"✅ 积分表已保存到项目内部：{standings_filename}")
    except Exception as e:
        print(f"❌ 抓取积分表失败：{str(e)}")
        return

 
    team_id_map = {}
    for team_entry in standings_data:
        team_id_map[team_entry["team"]["name"]] = team_entry["team"]["id"]
    
    recent_matches_all = {}
    for team_name, team_id in team_id_map.items():
        try:
            print(f"正在抓取 {team_name} 的近期比赛...")
            matches_url = f"{API_BASE_URL}/teams/{team_id}/matches"
            params = {"status": "FINISHED", "limit": 15}
            matches_resp = session.get(matches_url, headers=headers, params=params, timeout=30)
            matches_resp.raise_for_status()
            matches_data = matches_resp.json()["matches"]
            
          
            processed_matches = []
            for match in matches_data:
                home_team = match["homeTeam"]["name"]
                away_team = match["awayTeam"]["name"]
                full_time_score = match["score"]["fullTime"]
                
              
                is_home = (home_team == team_name)
          
                opponent = away_team if is_home else home_team
        
                if full_time_score["home"] > full_time_score["away"]:
                    result = "胜" if is_home else "负"
                elif full_time_score["home"] < full_time_score["away"]:
                    result = "负" if is_home else "胜"
                else:
                    result = "平"
                
                processed_matches.append({
                    "date": match["utcDate"],
                    "is_home": is_home,
                    "opponent": opponent,
                    "home_score": full_time_score["home"],
                    "away_score": full_time_score["away"],
                    "result": result
                })
            
            recent_matches_all[team_name] = processed_matches
            print(f"✅ 成功抓取 {team_name} 的近期比赛")
            
           
            time.sleep(REQUEST_DELAY)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"⚠️ {team_name} 抓取限流，延迟10秒后重试...")
                time.sleep(10)
            else:
                print(f"❌ {team_name} 抓取失败：{e.response.status_code} {e.response.reason}")
        except Exception as e:
            print(f"❌ {team_name} 抓取失败：{str(e)}")
            time.sleep(REQUEST_DELAY) 


    data_dir = get_internal_data_dir()
    today = datetime.now().strftime("%Y-%m-%d")
    matches_filename = os.path.join(data_dir, f"recent_matches_{today}.json")
    with open(matches_filename, "w", encoding="utf-8") as f:
        json.dump(recent_matches_all, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 近期比赛数据已保存到项目内部：{matches_filename}")

if __name__ == "__main__":
    main()