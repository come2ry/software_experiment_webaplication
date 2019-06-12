ソフトウェアコンピュータ実験
====

## Description
ソフトウェア実験の講義で作成したウェブアプリケーション
最初にMAX値とTURN_MAX値がランダムで決定され、ユーザーはNPCと各々のターンで1〜TURN_MAXまでの値をカウントしていき、
MAX値をカウントした方が負けとなる。勝者にはゲーム終了までにカウントしたポイント*100ポイントが与えられる。
なお、ユーザーは新規登録時には誰にも明かしたくない黒歴史一つと引き換えに、初期ポイントが5000ポイント与えられ、
他のユーザーの黒歴史を、そのユーザーの手持ちポイント*100ポイントを失うことで閲覧可能となる。
なお、ポイントを失うと当然自らの手持ちポイントが減る事になるので、自らの黒歴史が閲覧されやすくなることは言うまでもない。

>“Beware that, when fighting monsters, you yourself do not become a monster… for when you gaze long into the abyss. The abyss gazes also into you.”
>怪物と戦う者は、その過程で自分自身も怪物になることのないように気をつけなくてはならない。
>深淵をのぞく時、深淵もまたこちらをのぞいているのだ。
>
>        -フリードリヒ・ニーチェ （1844年～1900年）

## Requirement
bcrypt

## Usage
python3 run.py

## Author
tanaka raiki
