"""Generate demo certificate samples for live testing."""
import os
import fitz

def create_demo_files():
    os.makedirs("demo_samples", exist_ok=True)

    # 1. Authentic Sample Certificate
    doc1 = fitz.open()
    page1 = doc1.new_page(width=600, height=800)
    
    # Border
    rect = fitz.Rect(30, 30, 570, 770)
    page1.draw_rect(rect, color=(0.1, 0.3, 0.6), width=2)
    
    # Title & Text
    page1.insert_text((150, 100), "DELHI TECHNOLOGICAL UNIVERSITY", fontsize=16, fontname="helv", color=(0.05, 0.2, 0.5))
    page1.insert_text((210, 130), "(Formerly Delhi College of Engineering)", fontsize=10, fontname="helv", color=(0.3, 0.3, 0.3))
    page1.insert_text((180, 200), "BACHELOR OF TECHNOLOGY", fontsize=18, fontname="helv", color=(0.1, 0.1, 0.1))
    page1.insert_text((220, 230), "Computer Science & Engineering", fontsize=12, fontname="helv", color=(0.2, 0.4, 0.7))
    
    body = (
        "This is to certify that Rahul Kaushik bearing Roll No: 2K20/CO/345\n"
        "has successfully completed the prescribed curriculum and fulfilled\n"
        "all academic requirements for the award of the Degree.\n\n"
        "Cumulative Grade Point Average (CGPA): 8.85 / 10.0\n"
        "Division: First Class with Distinction\n"
        "Date of Issue: 24th June 2024\n"
        "Certificate No: DTU-2024-ENG-08912"
    )
    page1.insert_text((80, 320), body, fontsize=12, fontname="helv", color=(0.1, 0.1, 0.1))
    
    # Signatures
    page1.insert_text((80, 680), "Registrar", fontsize=11, fontname="helv", color=(0.3, 0.3, 0.3))
    page1.insert_text((420, 680), "Vice Chancellor", fontsize=11, fontname="helv", color=(0.3, 0.3, 0.3))
    
    auth_path = os.path.join("demo_samples", "authentic_btech_degree.pdf")
    doc1.save(auth_path)
    doc1.close()

    # 2. Tampered Sample Certificate (Irregular fonts, Photoshop metadata tag, pasted grade)
    doc2 = fitz.open()
    doc2.set_metadata({
        "producer": "Adobe Photoshop CC 2023 (Windows)",
        "creator": "Adobe Photoshop CC 2023",
        "creationDate": "D:20240624100000",
        "modDate": "D:20240624090000"  # mod date earlier than creation date (anomaly)
    })
    page2 = doc2.new_page(width=600, height=800)
    
    rect2 = fitz.Rect(30, 30, 570, 770)
    page2.draw_rect(rect2, color=(0.6, 0.1, 0.1), width=2)
    
    page2.insert_text((160, 100), "STATE INSTITUTE OF TECHNOLOGY", fontsize=16, fontname="helv", color=(0.1, 0.1, 0.1))
    page2.insert_text((190, 190), "PROVISIONAL CERTIFICATE", fontsize=16, fontname="helv", color=(0.6, 0.1, 0.1))
    
    body_tampered = (
        "Certified that Rohan Verma bearing Roll No: 18ME109\n"
        "was awarded Bachelor of Technology in Mechanical Engineering.\n\n"
        "Modified CGPA: 9.95 / 10.0\n"
        "Date of Issue: 10-08-2022\n"
        "Certificate No: SIT-CERT-44102"
    )
    page2.insert_text((80, 300), body_tampered, fontsize=12, fontname="helv", color=(0.1, 0.1, 0.1))
    
    # Insert contrasting patch / overlay to simulate paste
    patch_rect = fitz.Rect(75, 450, 525, 520)
    page2.draw_rect(patch_rect, color=(0.8, 0.8, 0.8), fill=(0.95, 0.95, 0.95), width=1)
    page2.insert_text((85, 490), "Tampered Division Stamp: First Class Honors Distinction", fontsize=14, fontname="times-bold", color=(0.8, 0.1, 0.1))
    
    tampered_path = os.path.join("demo_samples", "tampered_certificate_sample.pdf")
    doc2.save(tampered_path)
    doc2.close()

    print(f"Generated demo samples:\n - {auth_path}\n - {tampered_path}")

if __name__ == "__main__":
    create_demo_files()
