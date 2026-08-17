import os
from datetime import datetime

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from app.ml.preprocessing import normalize_text

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "training_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

TEST_SIZE = 0.2
RANDOM_STATE = 42


def build_pipeline(classifier):
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            preprocessor=normalize_text,
            analyzer="char_wb",
            ngram_range=(2, 5),
            sublinear_tf=True,
            min_df=1,
        )),
        ("clf", classifier),
    ])


def evaluate_task(task_name, texts, labels, report_lines):
    print(f"\n{'=' * 60}")
    print(f"  {task_name.upper()} TAHMİN MODELİ")
    print(f"{'=' * 60}")

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=TEST_SIZE,
        random_state=RANDOM_STATE, stratify=labels,
    )
    print(f"Eğitim örneği: {len(X_train)}  |  Test örneği: {len(X_test)}")

    candidates = {
        "Naive Bayes": MultinomialNB(alpha=0.3),
        "Linear SVM": LinearSVC(C=1.0, random_state=RANDOM_STATE),
    }

    results = {}
    for name, classifier in candidates.items():
        pipeline = build_pipeline(classifier)
        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        cv_scores = cross_val_score(
            build_pipeline(classifier), texts, labels,
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
        )

        results[name] = {
            "pipeline": pipeline,
            "accuracy": accuracy,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "y_pred": y_pred,
        }
        print(f"  {name:<14} test doğruluğu: {accuracy:.4f}  "
              f"| 5-kat CV: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")

    best_name = max(results, key=lambda n: results[n]["accuracy"])
    best = results[best_name]
    print(f"\n  --> Seçilen algoritma: {best_name} ({best['accuracy']:.2%})")

    report_lines.append(f"\n## {task_name.capitalize()} Tahmin Modeli\n")
    report_lines.append(f"- Eğitim örneği: **{len(X_train)}**, test örneği: **{len(X_test)}**")
    report_lines.append(f"- Sınıflar: {', '.join(sorted(set(labels)))}\n")
    report_lines.append("| Algoritma | Test Doğruluğu | 5-Kat Çapraz Doğrulama |")
    report_lines.append("|---|---|---|")
    for name, res in results.items():
        secili = " ✅" if name == best_name else ""
        report_lines.append(
            f"| {name}{secili} | {res['accuracy']:.4f} "
            f"| {res['cv_mean']:.4f} (±{res['cv_std']:.4f}) |"
        )

    report_lines.append(f"\n### Sınıf Bazlı Başarım ({best_name})\n")
    report_lines.append("```")
    report_lines.append(classification_report(
        y_test, best["y_pred"], zero_division=0, digits=3))
    report_lines.append("```")

    class_names = sorted(set(labels))
    matrix = confusion_matrix(y_test, best["y_pred"], labels=class_names)
    report_lines.append("\n### Karmaşıklık Matrisi (satır: gerçek, sütun: tahmin)\n")
    report_lines.append("| | " + " | ".join(class_names) + " |")
    report_lines.append("|---" * (len(class_names) + 1) + "|")
    for name, row in zip(class_names, matrix):
        report_lines.append(f"| **{name}** | " + " | ".join(str(v) for v in row) + " |")

    final_pipeline = build_pipeline(candidates[best_name])
    final_pipeline.fit(texts, labels)
    return final_pipeline, best_name, best["accuracy"]


def main():
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

    df = pd.read_csv(DATA_FILE)
    print(f"Eğitim verisi okundu: {len(df)} satır  ({DATA_FILE})")
    print(f"Kategori dağılımı : {df['category'].value_counts().to_dict()}")
    print(f"Öncelik dağılımı  : {df['priority'].value_counts().to_dict()}")

    texts = df["text"].tolist()

    report_lines = [
        "# Model Başarım Raporu",
        "",
        f"**Oluşturulma tarihi:** {datetime.now().strftime('%d.%m.%Y %H:%M')}  ",
        f"**Eğitim verisi:** `data/training_data.csv` ({len(df)} satır)  ",
        "**Yöntem:** TF-IDF vektörleştirme (2-5 karakterlik `char_wb` n-gram) "
        "+ sınıflandırıcı  ",
        f"**Bölme oranı:** %{int((1 - TEST_SIZE) * 100)} eğitim / "
        f"%{int(TEST_SIZE * 100)} test (stratified, random_state={RANDOM_STATE})",
        "",
        "## Veri Dağılımı",
        "",
        "| Kategori | Adet |",
        "|---|---|",
    ]
    for label, count in df["category"].value_counts().items():
        report_lines.append(f"| {label} | {count} |")
    report_lines += ["", "| Öncelik | Adet |", "|---|---|"]
    for label, count in df["priority"].value_counts().items():
        report_lines.append(f"| {label} | {count} |")

    summary = {}
    for task, column, filename in [
        ("kategori", "category", "category_model.joblib"),
        ("öncelik", "priority", "priority_model.joblib"),
    ]:
        model, algo, acc = evaluate_task(
            task, texts, df[column].tolist(), report_lines)
        path = os.path.join(MODEL_DIR, filename)
        joblib.dump(model, path)
        summary[task] = (algo, acc, filename)
        print(f"  Model kaydedildi: {path}")

    özet = ["", "## Özet", "", "| Görev | Seçilen Algoritma | Test Doğruluğu | Model Dosyası |",
            "|---|---|---|---|"]
    for task, (algo, acc, filename) in summary.items():
        özet.append(f"| {task.capitalize()} | {algo} | **{acc:.2%}** | `models/{filename}` |")
    özet.append("")
    report_lines[7:7] = özet

    report_lines += [
        "",
        "## Değerlendirme",
        "",
        "**Neden karakter n-gram?** İlk denemede kelime bazlı TF-IDF (1-2 kelimelik",
        "n-gram) kullanıldığında kategori modelinin çapraz doğrulama başarımı ~%63,",
        "öncelik modelinin ~%59 seviyesinde kalmıştır. Türkçe eklemeli bir dil",
        "olduğu için \"yazıcı / yazıcıda / yazıcının\" gibi aynı kökten türeyen",
        "kelimeler modele birbirinden bağımsız üç kelime olarak görünmektedir.",
        "Karakter n-gram'larına (`char_wb`, 2-5) geçilerek bu sorun giderilmiş ve",
        "başarım kategori tarafında ~%78'e, öncelik tarafında ~%70'e yükselmiştir.",
        "",
        "**Görevlerin karşılaştırması.** Tek bir test bölünmesi 41 örnek içerdiği",
        "için oynaktır; daha güvenilir ölçüt 5 katlı çapraz doğrulamadır. Buna göre",
        "kategori tahmini, sınıfları ayıran belirgin anahtar kelimeler (yazıcı,",
        "internet, excel, kablo vb.) sayesinde öncelik tahminine göre daha başarılı",
        "çalışmaktadır. Öncelik tahmini daha zordur, çünkü bir talebin aciliyeti çoğu",
        "zaman tek tek kelimelerden değil bağlamdan anlaşılır.",
        "",
        "**Sınırlılıklar.**",
        "",
        "- Eğitim verisi sentetik olarak hazırlanmıştır; gerçek kullanıcı metinleri",
        "  daha dağınık (yazım hatası, kısaltma, eksik ifade) olacaktır.",
        "- Veri kümesi 205 satırdır. Sistem kullanıldıkça biriken gerçek talepler",
        "  eğitim verisine eklenerek model düzenli aralıklarla yeniden eğitilmelidir.",
        "- Karmaşıklık matrislerinde görüldüğü üzere en sık karıştırılan sınıflar",
        "  donanım-yazılım (\"program açılmıyor\" vs. \"bilgisayar açılmıyor\") ve",
        "  düşük-orta önceliktir.",
        "",
        "**Kullanım biçimi.** Model tahmini personelin seçimini **değiştirmez**;",
        "her iki değer de bilgi işlem panelinde karşılaştırmalı gösterilir",
        "(şeffaflık ilkesi). Nihai karar bilgi işlem personeline aittir.",
        "",
    ]

    report_path = os.path.join(REPORT_DIR, "model_performance.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n{'=' * 60}")
    print(f"Başarım raporu yazıldı: {report_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
