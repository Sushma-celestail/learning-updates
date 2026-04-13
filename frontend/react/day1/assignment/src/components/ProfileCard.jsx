import React from 'react'

const ProfileCard = ({ name, title, bio, avatarUrl }) => {
  return (
  <div
  style={{
        display: "flex",
    flexDirection: "row", // 👈 THIS makes cards in one row
    gap: "20px",
    justifyContent: "center",
  }}
>
  <img
    src={avatarUrl}
    alt={name}
    style={{
      width: "100px",
      height: "100px",
      borderRadius: "50%", // 👈 circular image
      objectFit: "cover",
      marginBottom: "12px",
    }}
  />

  <h3 style={{ margin: "8px 0", fontSize: "18px", fontWeight: "600" }}>
    {name}
  </h3>

  <p style={{ margin: "4px 0", color: "#6b7280", fontSize: "14px" }}>
    {title}
  </p>

  <p style={{ marginTop: "8px", fontSize: "13px", color: "#374151" }}>
    {bio}
  </p>
</div>
  );
};

export default ProfileCard;