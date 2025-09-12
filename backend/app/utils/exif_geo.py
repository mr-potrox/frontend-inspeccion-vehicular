import io, math
from typing import Optional, Tuple, List, Dict
from PIL import Image, ExifTags

_GPS_TAG = None
for k,v in ExifTags.TAGS.items():
    if v=="GPSInfo":
        _GPS_TAG=k
        break

def _deg(value):
    try:
        d=value[0][0]/value[0][1]
        m=value[1][0]/value[1][1]
        s=value[2][0]/value[2][1]
        return d+m/60+s/3600
    except:
        return None

def extract_exif_geo(image_bytes: bytes)->Optional[Tuple[float,float]]:
    try:
        img=Image.open(io.BytesIO(image_bytes))
        exif=img._getexif()
        if not exif or _GPS_TAG not in exif: return None
        gps_raw=exif[_GPS_TAG]
        gps={}
        for k,v in ExifTags.GPSTAGS.items():
            if k in gps_raw:
                gps[v]=gps_raw[k]
        lat=gps.get("GPSLatitude"); lon=gps.get("GPSLongitude")
        latr=gps.get("GPSLatitudeRef"); lonr=gps.get("GPSLongitudeRef")
        if not (lat and lon and latr and lonr): return None
        latd=_deg(lat); lond=_deg(lon)
        if latd is None or lond is None: return None
        if latr!="N": latd=-latd
        if lonr!="E": lond=-lond
        return (round(latd,7), round(lond,7))
    except:
        return None

def haversine_meters(a_lat,a_lon,b_lat,b_lon):
    R=6371000
    dlat=math.radians(b_lat-a_lat)
    dlon=math.radians(b_lon-a_lon)
    A=math.sin(dlat/2)**2+math.cos(math.radians(a_lat))*math.cos(math.radians(b_lat))*math.sin(dlon/2)**2
    c=2*math.atan2(math.sqrt(A), math.sqrt(1-A))
    return R*c

def geo_stats(points: List[Tuple[float,float]])->Dict:
    if not points: return {"count":0,"max_dist":0,"min_dist":0,"pairs":0}
    if len(points)==1: return {"count":1,"max_dist":0,"min_dist":0,"pairs":0}
    maxd=0; mind=1e12; pairs=0
    for i in range(len(points)):
        for j in range(i+1,len(points)):
            d=haversine_meters(points[i][0],points[i][1],points[j][0],points[j][1])
            maxd=max(maxd,d); mind=min(mind,d); pairs+=1
    return {"count":len(points),"max_dist":round(maxd,2),"min_dist":round(mind if mind<1e11 else 0,2),"pairs":pairs}