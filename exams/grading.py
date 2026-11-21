# Letter grades like Nepal's NEB: (minimum percentage, grade), highest first
GRADE_SCALE = [
    (90, 'A+'),
    (80, 'A'),
    (70, 'B+'),
    (60, 'B'),
    (50, 'C+'),
    (40, 'C'),
    (35, 'D'),
    (0, 'NG'),
]


def grade_for(percent):
    """75 → 'B+', 92.5 → 'A+', 20 → 'NG' (not graded)."""
    for minimum, grade in GRADE_SCALE:
        if percent >= minimum:
            return grade
    return 'NG'
