from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

# -----------------------------
# Report Sections (NEW TABLE)
# -----------------------------
class ReportSection(Base):
    __tablename__ = "report_sections"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), index=True)

    title = Column(String(255), index=True)
    content = Column(Text)
    order = Column(Integer)

    report = relationship("Report", backref="sections")
