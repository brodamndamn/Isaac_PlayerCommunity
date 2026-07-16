interface UserAvatarProps {
  avatar: string | null;
  username: string;
  size?: number;
}

export default function UserAvatar({ avatar, username, size = 22 }: UserAvatarProps) {
  const src = avatar ? `/uploads/${avatar}` : null;
  if (src) {
    return (
      <img
        src={src}
        alt={username}
        style={{
          width: size,
          height: size,
          borderRadius: "50%",
          objectFit: "cover",
          flexShrink: 0,
        }}
      />
    );
  }
  return (
    <span
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        background: "#6b3a2a",
        color: "#f5e6d0",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: size * 0.5,
        fontWeight: 700,
        flexShrink: 0,
      }}
    >
      {username[0]?.toUpperCase()}
    </span>
  );
}
