"use client";

export type Skill = "strategy-review" | "gender-tech-review" | "budget-review";

const SKILLS: { id: Skill; label: string; description: string }[] = [
  {
    id: "strategy-review",
    label: "Strategy",
    description: "General strategy analysis",
  },
  {
    id: "gender-tech-review",
    label: "Gender & Tech",
    description: "Gender equality & health equity",
  },
  {
    id: "budget-review",
    label: "Budget",
    description: "Funding & allocations",
  },
];

export function SkillSelector({
  selected,
  onSelect,
}: {
  selected: Skill;
  onSelect: (skill: Skill) => void;
}) {
  return (
    <div style={{ display: "flex", gap: "0.5rem" }}>
      {SKILLS.map((skill) => (
        <button
          key={skill.id}
          onClick={() => onSelect(skill.id)}
          title={skill.description}
          style={{
            padding: "0.35rem 0.75rem",
            fontSize: "0.8rem",
            fontWeight: 500,
            borderRadius: "var(--radius)",
            border: "1px solid",
            borderColor:
              selected === skill.id ? "var(--accent)" : "var(--border)",
            background:
              selected === skill.id
                ? "var(--accent-subtle)"
                : "var(--bg-secondary)",
            color:
              selected === skill.id
                ? "var(--accent)"
                : "var(--text-secondary)",
            cursor: "pointer",
            transition: "all 0.15s ease",
          }}
        >
          {skill.label}
        </button>
      ))}
    </div>
  );
}
