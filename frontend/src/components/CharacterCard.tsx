import { Link } from "react-router-dom";
import type { Character } from "../types/character";
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
      <div className={styles.topRow}>
        {character.image_url ? (
          <img
            src={`/images/${character.image_url}`}
            alt={character.name_cn}
            className={styles.thumb}
            data-item-id={character.id}
          />
        ) : (
          <div className={styles.thumbPlaceholder} data-item-id={character.id} />
        )}
        <div className={styles.titleCol}>
          <div className={styles.header}>
            <span className={styles.id}>#{character.id}</span>
            {character.is_tainted && <span className={styles.tag}>里</span>}
          </div>
          <div className={styles.nameRow}>
            <h3 className={styles.name}>{character.name_cn}</h3>
            <span className={styles.health}>
              <span className={styles.statIcon} data-heart="health" />
              {character.health}
            </span>
          </div>
          <div className={styles.nameEnRow}>
            <p className={styles.nameEn}>{character.name_en}</p>
            {character.damage != null && (
              <span className={styles.damage}>
                <span className={styles.statIcon} data-stat="damage" />
                {character.damage}
              </span>
            )}
          </div>
        </div>
      </div>
      {character.description && (
        <p className={styles.desc}>{character.description}</p>
      )}
    </Link>
  );
}
