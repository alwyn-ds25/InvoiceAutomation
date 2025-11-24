from invoice_core_processor.core.database import get_postgres_connection

def get_high_impact_kpis() -> dict:
    """Calculates and returns the high-impact KPIs."""
    conn = None
    try:
        conn = get_postgres_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM invoices;")
            total_invoices = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM invoices WHERE status = 'SYNCED_SUCCESS';")
            successful_syncs = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM invoices WHERE status = 'VALIDATED_FLAGGED';")
            flagged_invoices = cur.fetchone()[0]

            cur.execute("SELECT SUM(grand_total) FROM invoices WHERE status = 'SYNCED_SUCCESS';")
            total_invoice_value = cur.fetchone()[0] or 0.0

        return {
            "total_invoices": total_invoices,
            "successful_syncs": successful_syncs,
            "flagged_invoices": flagged_invoices,
            "total_invoice_value": float(total_invoice_value)
        }
    finally:
        if conn: conn.close()

def get_quality_efficiency_kpis() -> dict:
    """Calculates and returns the quality and efficiency KPIs."""
    conn = None
    try:
        conn = get_postgres_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT AVG(extraction_confidence) FROM invoices;")
            ocr_accuracy = (cur.fetchone()[0] or 0.0) * 100

            cur.execute("""
                SELECT
                    CAST(SUM(CASE WHEN status = 'VALIDATED_CLEAN' THEN 1 ELSE 0 END) AS FLOAT) * 100 / COUNT(*)
                FROM invoices WHERE status IN ('VALIDATED_CLEAN', 'VALIDATED_FLAGGED');
            """)
            pass_rate_result = cur.fetchone()
            validation_pass_rate = pass_rate_result[0] if pass_rate_result else 0.0

            cur.execute("SELECT AVG(processing_duration_ms) FROM invoices WHERE processing_duration_ms IS NOT NULL;")
            avg_processing_time = cur.fetchone()[0] or 0.0

        return {
            "ocr_accuracy": f"{ocr_accuracy:.2f}%",
            "validation_pass_rate": f"{validation_pass_rate:.2f}%",
            "avg_processing_time_ms": int(avg_processing_time)
        }
    finally:
        if conn: conn.close()

def get_deep_insights() -> dict:
    """Returns placeholder data for deep insights."""
    return {
        "spend_by_vendor": {"Vendor A": 1000, "Vendor B": 2000},
        "spend_by_category": {"Software": 1500, "Marketing": 1500},
        "duplicate_detection_rate": "5.2%"
    }

def get_all_metrics() -> dict:
    """Combines all KPIs into a single dictionary."""
    return {
        "high_impact_kpis": get_high_impact_kpis(),
        "quality_efficiency": get_quality_efficiency_kpis(),
        "deep_insights": get_deep_insights()
    }
