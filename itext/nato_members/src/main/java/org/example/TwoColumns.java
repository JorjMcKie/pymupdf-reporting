package org.example;

import com.itextpdf.html2pdf.HtmlConverter;
import com.itextpdf.io.font.constants.StandardFonts;
import com.itextpdf.kernel.font.PdfFont;
import com.itextpdf.kernel.font.PdfFontFactory;
import com.itextpdf.kernel.geom.PageSize;
import com.itextpdf.kernel.geom.Rectangle;
import com.itextpdf.kernel.pdf.PdfDocument;
import com.itextpdf.kernel.pdf.PdfWriter;
import com.itextpdf.layout.*;
import com.itextpdf.layout.ColumnDocumentRenderer;
import com.itextpdf.layout.element.*;
import com.itextpdf.layout.hyphenation.HyphenationConfig;
import com.itextpdf.layout.properties.TextAlignment;

import java.io.IOException;

public class TwoColumns {

    public static void main(String[] args) throws IOException {
        //Initialize PDF document
        PdfDocument pdf = new PdfDocument(new PdfWriter("two_columns.pdf"));

        // Initialize document
        Document document = new Document(pdf, PageSize.LETTER, false);

        //Set column parameters
        float offSet = 36;
        float gutter = 20;
        float columnWidth = (PageSize.LETTER.getWidth() - offSet * 2) / 2 - gutter;
        float columnHeight = PageSize.LETTER.getHeight() - offSet * 2;

        //Define column areas
        Rectangle[] columns = {
                new Rectangle(offSet, offSet, columnWidth, columnHeight),
                new Rectangle(offSet + columnWidth + gutter, offSet, columnWidth, columnHeight)};

        PdfFont font = PdfFontFactory.createFont(StandardFonts.TIMES_ROMAN);
        document.setTextAlignment(TextAlignment.JUSTIFIED)
                .setFont(font)
                .setHyphenation(new HyphenationConfig("en", null, 3, 3));

        // Set renderer
        document.setRenderer(new ColumnDocumentRenderer(document, columns));

        // Add elements
        for (IElement element : HtmlConverter.convertToElements(TwoColumns.class.getResourceAsStream("/springer.html"))) {
            document.add((IBlockElement)element);
        }

        //Close document
        document.close();
    }
}