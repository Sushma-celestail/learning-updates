function ProfileCard({name, title, bio, avatarUrl,age,email}){
    return(
        <div className="card">
            <img src={avatarUrl} alt={name} className="avatar"/>
            <h2>{name}</h2>
            <h4>{title}</h4>
            <p>{bio}</p>
            <p>Age:{age}</p>
            <p>Email:{email}</p>
            <p>Status: {age>=18?"Adult":"Minor"}</p>
        </div>
    );
}
export default ProfileCard;