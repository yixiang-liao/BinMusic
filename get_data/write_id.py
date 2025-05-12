from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.model.artists import Artist  # 依照你實際路徑修改
import json

artist_id = {
                    "麋先生":{"spotify":["4AWa6pcQK9J9aSAN67cLHv"] , "kkbox":["OolqHd87hVgge-KSt3"] ,"apple_music":["976685640"] , "youtube":["@Mixerband"] } , 
                    "五月天":{"spotify":["16s0YTFcyjP4kgFwt7ktrY"], "kkbox":["9XN-7yg5vg3gYnCdsM"] ,"apple_music":["369211611"] , "youtube":[""] }, 
                    "李宗盛":{"spotify":["2TXF68WgfTZlipUvLBsQre" , "33WcohNHOZ7pGy3Ep5c3xf"], "kkbox":["0t9cKqeq91sO_KqRW7"] ,"apple_music":["152417293"] , "youtube":[""] } , 
                    "劉若英" :{"spotify":["6qzfo7jiO4OrhxrvPFPlWX"], "kkbox":["P_TzVt5yVKWxssrLJs"] ,"apple_music":["16027938"] , "youtube":["@NANARENELIU"] } , 
                    "蘇慧倫" :{"spotify":["0HT1FqSMdbL40XGpLcLnoF"], "kkbox":["SkvRUWHwT10-ltsz29"] ,"apple_music":["152149547"] , "youtube":["@tarcysu4654"] } , 
                    "丁噹" :{"spotify":["1EUq1MC4vfYYxcVK9aJnXf"], "kkbox":["9_w6azeJGTMFKInhqn"] ,"apple_music":["453466412"] , "youtube":["@dellading6946"] } , 
                    "告五人" :{"spotify":["6xErgeZYatiaQ36SB5bvi8"], "kkbox":["9ZHTY_i6Jj_jI2Evam"] ,"apple_music":["1284151651"] , "youtube":["@Accusefive"] } , 
                    "宇宙人" : {"spotify":["0tNjyz75Px29Yuf1sjs25G"], "kkbox":["Lai8PoHfMgHOt_XWaz"] ,"apple_music":["369125109"] , "youtube":["@CosmosPeople"] } , 
                    "家家" : {"spotify":["5qUYuf6cIHU241KxPyDMBp"], "kkbox":["Ha2Fxn0Ll3jmrS4hLj"] ,"apple_music":["295060477"] , "youtube":["@jiajiachimusic"] } , 
                    "蕭秉治" : {"spotify":["0Ej4GfzIcW3dWP0rC5d4x1"], "kkbox":["Okn41XNM0d0goNRbqH"] ,"apple_music":["1385500292"] , "youtube":["@xiaobingchih7788"] } , 
                    "鼓鼓 呂思緯" : {"spotify":["2QOj4jFuDei3DWSkDHfWTm"], "kkbox":["GqOipgigyaDAnz1DnF"] ,"apple_music":["592113508"] , "youtube":["@gboyswag6504"] } , 
                    "白安" : {"spotify":["6ytn3LGlsoOgU3YGF9T42s"], "kkbox":["4kLdMnxqN3_1LEXw5k"] ,"apple_music":["904392836"] , "youtube":["@baiannmusic"] } , 
                    "李劍青" : {"spotify":["5pivVtnHiM5CUInXsqKmfy"], "kkbox":["8oNOjctmEEYzjL5ML4"] ,"apple_music":["311147960"] , "youtube":[""] } , 
                    "Tizzy Bac" : {"spotify":["6Rv0ndBVPEQJ7KagPDtC5H"], "kkbox":["Gr7FGJYEMQFlP9jpy-"] ,"apple_music":["308554746"] , "youtube":["@TizzyBac"] } , 
                    "Energy" :{"spotify":["6GUGvmk5XZesTWRQdkp69u"], "kkbox":["_X8_34d2rOJkly58E2"] ,"apple_music":["1528971960"] , "youtube":[""] }
}

def safe_json_str(lst):
    """非空 list 則轉為 JSON 字串，否則回傳 None"""
    return json.dumps(lst) if lst else None

def update_artists():
    db: Session = SessionLocal()
    try:
        for name, ids in artist_id.items():
            artist = db.query(Artist).filter_by(name=name).first()
            if artist:
                artist.spotify_id = safe_json_str(ids.get("spotify"))
                artist.kkbox_id = safe_json_str(ids.get("kkbox"))
                artist.apple_music = safe_json_str(ids.get("apple_music"))
                artist.youtube_id = safe_json_str(ids.get("youtube"))
                print(f"✅ 更新：{name}")
            else:
                print(f"⚠️ 找不到藝人：{name}，未更新")
        db.commit()
        print("✅ 所有資料更新完成")
    except Exception as e:
        db.rollback()
        print("❌ 發生錯誤：", e)
    finally:
        db.close()


if __name__ == "__main__":
    update_artists()