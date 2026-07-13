import { Link } from "react-router-dom";
import type { Character } from "../types/character";
import HealthHearts from "./HealthHearts";
import styles from "./CharacterCard.module.css";

interface CharacterCardProps {
  character: Character;
}

export default function CharacterCard({ character }: CharacterCardProps) {
  return (
    <Link
      to={`/characters/${character.id}`}
      className={`${styles.card} ${character.is_tainted ? styles.tainted : ""}`}
    >
      <div className={styles.header}>
        <span className={styles.id}>#{character.id}</span>
        {character.is_tainted && <span className={styles.tag}>里</span>}
      </div>
      <h3 className={styles.name}>{character.name_cn}</h3>
      <p className={styles.nameEn}>{character.name_en}</p>
      <div className={styles.stats}>
        <span><HealthHearts health={character.health} /></span>
        {character.damage != null && <span>⚔ {character.damage}</span>}
      </div>
      {character.description && (
        <p className={styles.desc}>{character.description}</p>
      )}
    </Link>
  );
}
