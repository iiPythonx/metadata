FIELD_INDEX = {
    "DISC":                         lambda a, t: t["disc"],
    "ALBUM":                        lambda a, t: a["title"],
    "TRACK":                        lambda a, t: t["position"],
    "TITLE":                        lambda a, t: t["recording"]["title"],
    "ARTIST":                       lambda a, t: [artist["artist"]["name"] for artist in t["artist-credit"]],
    "ALBUMARTIST":                  lambda a, t: [artist["artist"]["name"] for artist in a["artist-credit"]],
    "MUSICBRAINZ_ALBUMID":          lambda a, t: a["id"],
    "MUSICBRAINZ_ALBUMARTISTID":    lambda a, t: a["artist-credit"][0]["artist"]["id"],
    "MUSICBRAINZ_TRACKID":          lambda a, t: t["recording"]["id"],
    "MUSICBRAINZ_RELEASETRACKID":   lambda a, t: t["id"]
}
