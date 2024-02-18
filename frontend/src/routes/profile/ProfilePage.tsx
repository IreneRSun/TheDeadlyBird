import React, { useState, useEffect, lazy } from 'react';

import { publicDir } from "../../constants";

import Page from '../../components/layout/Page';

import styles from './ProfilePage.module.css';
import { useParams } from 'react-router-dom';
import { getAuthor } from '../../api/authors';
import { getUserId } from '../../utils/auth';
import { apiDeleteFollower, apiFollowRequest, apiGetFollower, apiGetFollowing } from '../../api/following';

enum FollowState {
    FOLLOWING="following",
    PENDING="pending",
    NOT_FOLLOWING="not_following"
};

const ProfilePage: React.FC = () => {
    // GET request on user to request actual API?...
    const [authorId, setAuthorId] = useState<string>("");
    const [avatarURL, setAvatarURL] = useState(`${publicDir}/static/default-avatar.png`);
    const [githubUsername, setGithubUsername] = useState("");
    const [username, setUsername] = useState("");
    const [bio, setBio] = useState("I don't really know what I'm doing...");     // TODO: Do we want a bio?
    const [postCount, setPostCount] = useState(-1);
    const [followingCount, setFollowingCount] = useState(-1);
    const [followerCount, setFollowerCount] = useState(-1);
    const [followState, setFollowState] = useState<FollowState>(FollowState.NOT_FOLLOWING)

    const curAuthorId : string = getUserId().toString(); 
    const params = useParams();

    useEffect(() => {
        const userId = params["id"];
        getAuthor(parseInt(userId as string))
            .then(async author => {
                if (!author) {
                    console.error(`Failed to load user profile: ${userId}`);
                    return;
                }

                setUsername(author.displayName);
                setPostCount(author.posts);
                setFollowerCount(author.followers);
                setFollowingCount(author.following);
                setAuthorId(author.id);

                if (author.github) {
                    setGithubUsername(author.github);
                }
                if (author.profileImage) {
                    setAvatarURL(author.profileImage);
                }
            });
        
        if (userId) {
            apiGetFollower(userId, curAuthorId)
            .then(async response => {
                console.log(response);
                if (response.items && response.items.length !== 0) { 
                    setFollowState(FollowState.FOLLOWING);
                }
            });
        }
         
    }, [params]);

    const handleFollow = async () => {
        if (followState == FollowState.NOT_FOLLOWING) {
            const responseJSON = await apiFollowRequest(curAuthorId, authorId);
            if (!responseJSON["error"]) {
                setFollowState(FollowState.PENDING);
                console.log(followState);
            }
        } else if (followState == FollowState.FOLLOWING) {
            const responseJSON = await apiDeleteFollower(authorId, curAuthorId);
            if (!responseJSON["error"]) {
                setFollowState(FollowState.NOT_FOLLOWING);
            }
        }
        
    }

    return <Page>
        <div id={styles.container}>
            <div id={styles.header} style={{ position: "relative" }}>
                <div id={styles.avatarContainer}>
                    <img alt="Profile Avatar" src={avatarURL} />
                </div>
                <div id={styles.identityContainer}>
                    <h1 id={styles.username}>{username}</h1>
                    <h5 id={styles.bio}>{bio}</h5>
                </div>
                <div id={styles.statsAndFollow}>
                    <div className={styles.item}>
                        <div id={styles.followButton}
                            onClick={handleFollow} 
                        >
                            {followState === FollowState.FOLLOWING ?  
                            "Unfollow" : 
                            followState === FollowState.PENDING ? 
                            "Pending" : "Follow"
                            }
                        </div>
                    </div>
                    <div className={styles.item}>
                        <div>
                            <span>Posts</span> <span className={styles.itemAmount}>{postCount === -1 ? "" : postCount}</span>
                        </div>
                    </div>
                    <div className={styles.item}>
                        <div>
                            <span>Following</span> <span className={styles.itemAmount}>{followingCount === -1 ? "" : followingCount}</span>
                        </div>
                    </div>
                    <div className={styles.item}>
                        <div>
                            <span>Followers</span> <span className={styles.itemAmount}>{followerCount === -1 ? "" : followerCount}</span>
                        </div>
                    </div>
                </div>
                {githubUsername ? (
                    <a href={`https://github.com/${githubUsername}`} target="_blank" rel="noreferrer">
                        <div id={styles.githubContainer}>
                            <img alt="Github Account" style={{ height: "100%", width: "100%" }} src={`${publicDir}/static/github.png`} />
                        </div>
                    </a>
                ) : null}
            </div>
            <div id={styles.feed}>
                {/* TODO: Profile feed */}
            </div>
        </div>
    </Page>;
};

export default ProfilePage;