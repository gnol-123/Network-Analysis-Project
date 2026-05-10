import sys, os, json
from pathlib import Path
import hashlib

from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID

# Parent directory & output file in artifact
project_root = Path(__file__).parent.parent

inputJson = project_root / "artifacts" / "youtubeData-metGala.json"
usersJson = project_root / "artifacts" / "indexes" / "users.json"
videoJson = project_root / "artifacts" / "indexes" / "videos.json"
commentsJson = project_root / "artifacts" / "indexes" / "comments.json"
channelsJson = project_root / "artifacts" / "indexes" / "channels.json"


from utils.utils import load, dump 

# index pipeline ----------------------------------------------------------------------------------------------------------------------------

def build(jFile=inputJson):
    """
    """

    # Load data
    data = load(jFile)
    print("Retrieved file")
    list_videos = data["videos"]

    users = {}
    channels = {}
    videos = {}
    comments = {} 

    print("Building dataframe...")
    print(f"Total of {len(data['videos'])}")

    for i, video in enumerate(data['videos'], start=1):


        # CHANNEL DICT --------------------------------------------------
        channelID = video["channelId"]
        channelName = video["channelTitle"]

        channelDict = channels.get(channelID, {})
        channelDict["name"] = channelName
        channelDict.setdefault("videos", []).append(video["videoId"])
        channels[channelID] = channelDict

        # VIDEO DICT ----------------------------------------------------

        videoID = video["videoId"]
        videoDict = videos.get(videoID, {})
        videoDict["title"]       = video["title"]
        videoDict["channelId"]   = video["channelId"]
        videoDict["publishedAt"] = video["publishedAt"]
        videoDict["viewCount"]   = video["viewCount"]
        videoDict["likeCount"]   = video["likeCount"]
        videoDict.setdefault("comments", [])
        videos[videoID] = videoDict

        # user dicts ---------------------------------------------------------------

        for j, comment in enumerate(video["comments"], start=1):

            commentID  = comment["commentId"]
            authorID   = comment["authorId"]

            commentDict = {}
            commentDict["text"]            = comment["text"]
            commentDict["publishedAt"]     = comment["publishedAt"]
            commentDict["likeCount"]       = comment["likeCount"]
            commentDict["totalReplyCount"] = comment.get("totalReplyCount", 0)
            commentDict["parentCommentId"] = comment.get("parentCommentId", None)
            commentDict["replyToAuthorId"] = comment.get("replyToAuthorId", None)
            commentDict["videoId"]         = comment["videoId"]
            commentDict["isReply"]         = comment["isReply"]
            commentDict["authorId"]        = authorID
            comments[commentID] = commentDict

            userDict = users.get(authorID, {})
            userDict["name"] = comment["author"]
            userDict.setdefault("comments", []).append(commentID)
            users[authorID] = userDict

            videos[videoID]["comments"].append(commentID)

        print(f"Done with video {i}")

    dump(users, outPath=usersJson)
    dump(videos, outPath=videoJson)
    dump(channels, outPath=channelsJson)
    dump(comments, outPath=commentsJson)

    return True

# main ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    print("Bulding indexes...")
    build(inputJson)
