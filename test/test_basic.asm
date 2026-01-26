; Generated 6502 Assembly Code
; Processor: 6502

    processor 6502
    org $0600    ; Start program at $0600

start:
    LDX #$FF
    TXS          ; Initialize stack pointer

    ; var x = <expression>
    LDA #$0A      ; Load literal 10
    STA $10        ; Store to x

    ; var y = <expression>
    LDA #$05      ; Load literal 5
    STA $11        ; Store to y

    ; var result = <expression>
    LDA #$00      ; Load literal 0
    STA $12        ; Store to result

    ; result = <expression>
    LDA $10        ; Load x
    PHA             ; Save left operand
    LDA $11        ; Load y
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    CLC
    ADC $FE         ; Add
    STA $12        ; Store to result

    ; output(<value>)
    LDA $12        ; Load result
    JSR output_routine


    BRK          ; End program

; ==================== I/O Routines ====================

; Target: py65mon emulator
; Console output at $F001, input at $F004

; Temporary storage for decimal output
OUTPUT_NUM = $01    ; Number to output
OUTPUT_DIGIT = $02  ; Current digit
SUPPRESS_ZERO = $03 ; Flag to suppress leading zeros

output_routine:
    ; Output value in A as decimal number (0-255)
    STA OUTPUT_NUM
    LDA #1
    STA SUPPRESS_ZERO  ; Start suppressing leading zeros

    ; Output hundreds digit
    LDA OUTPUT_NUM
    LDX #0           ; X will count hundreds
output_hundreds:
    CMP #100
    BCC output_hundreds_done
    SBC #100         ; Subtract 100 (carry is set)
    INX
    JMP output_hundreds
output_hundreds_done:
    STA OUTPUT_NUM   ; Save remainder
    TXA
    BEQ skip_hundreds ; Skip if zero
    LDA #0
    STA SUPPRESS_ZERO ; Found non-zero, stop suppressing
    TXA
    CLC
    ADC #48          ; Convert to ASCII
    STA $F001        ; Output hundreds digit
skip_hundreds:

    ; Output tens digit
    LDA OUTPUT_NUM
    LDX #0           ; X will count tens
output_tens:
    CMP #10
    BCC output_tens_done
    SBC #10          ; Subtract 10 (carry is set)
    INX
    JMP output_tens
output_tens_done:
    STA OUTPUT_NUM   ; Save remainder (ones digit)
    TXA
    BNE print_tens   ; Print if non-zero
    LDA SUPPRESS_ZERO
    BNE skip_tens    ; Skip if still suppressing zeros
print_tens:
    LDA #0
    STA SUPPRESS_ZERO ; Stop suppressing
    TXA
    CLC
    ADC #48          ; Convert to ASCII
    STA $F001        ; Output tens digit
skip_tens:

    ; Output ones digit (always output, even if zero)
    LDA OUTPUT_NUM
    CLC
    ADC #48          ; Convert to ASCII
    STA $F001        ; Output ones digit

    ; Output newline
    LDA #10
    STA $F001
    RTS

input_routine:
    ; Read character from py65mon console input
    LDA $F004       ; Read from console input
    SEC
    SBC #48         ; Convert from ASCII to number
    RTS
